"""
BusinessVerse - Machine Learning Utilities
Handles model training, prediction, and persistence for:
  - Sales Prediction       (Linear Regression)
  - Customer Churn         (Random Forest Classifier)
  - Customer Segmentation  (K-Means Clustering)
"""

import os
import numpy as np
import pandas as pd
import joblib
from pathlib import Path

from sklearn.linear_model    import LinearRegression
from sklearn.ensemble        import RandomForestClassifier
from sklearn.cluster         import KMeans
from sklearn.model_selection import train_test_split
from sklearn.preprocessing   import StandardScaler, LabelEncoder
from sklearn.metrics         import (mean_absolute_error, mean_squared_error,
                                     r2_score, accuracy_score,
                                     classification_report)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR    = Path(__file__).resolve().parent.parent.parent
MODELS_DIR  = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

SALES_MODEL_PATH      = MODELS_DIR / "sales_model.pkl"
SALES_SCALER_PATH     = MODELS_DIR / "sales_scaler.pkl"
CHURN_MODEL_PATH      = MODELS_DIR / "churn_model.pkl"
CHURN_SCALER_PATH     = MODELS_DIR / "churn_scaler.pkl"
SEGMENT_MODEL_PATH    = MODELS_DIR / "segment_model.pkl"
SEGMENT_SCALER_PATH   = MODELS_DIR / "segment_scaler.pkl"


# ===========================================================================
# A. SALES PREDICTION  — Linear Regression
# ===========================================================================

def prepare_sales_features(orders_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate orders into monthly features for regression."""
    df = orders_df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month_num"]  = df["order_date"].dt.year * 12 + df["order_date"].dt.month

    monthly = df.groupby("month_num").agg(
        total_revenue  = ("revenue",  "sum"),
        total_orders   = ("order_id", "count"),
        total_quantity = ("quantity", "sum"),
        avg_discount   = ("discount", "mean"),
    ).reset_index()

    # Lag features
    monthly["lag1_revenue"] = monthly["total_revenue"].shift(1)
    monthly["lag2_revenue"] = monthly["total_revenue"].shift(2)
    monthly["rolling_mean"] = monthly["total_revenue"].rolling(3).mean()
    monthly = monthly.dropna().reset_index(drop=True)
    return monthly


def train_sales_model(orders_df: pd.DataFrame) -> dict:
    """Train Linear Regression for monthly sales prediction. Returns metrics dict."""
    monthly = prepare_sales_features(orders_df)
    if len(monthly) < 6:
        return {"error": "Not enough data (need ≥ 6 months)."}

    feature_cols = ["month_num", "lag1_revenue", "lag2_revenue", "rolling_mean",
                    "total_orders", "total_quantity", "avg_discount"]
    X = monthly[feature_cols].values
    y = monthly["total_revenue"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    model = LinearRegression()
    model.fit(X_train_s, y_train)

    y_pred = model.predict(X_test_s)
    metrics = {
        "MAE":  round(mean_absolute_error(y_test, y_pred), 2),
        "RMSE": round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),
        "R2":   round(r2_score(y_test, y_pred), 4),
    }

    joblib.dump(model,  SALES_MODEL_PATH)
    joblib.dump(scaler, SALES_SCALER_PATH)
    return {"metrics": metrics, "monthly_df": monthly, "feature_cols": feature_cols}


def predict_sales(months_ahead: int = 6) -> pd.DataFrame:
    """Predict next N months of revenue using the trained model."""
    if not SALES_MODEL_PATH.exists():
        return pd.DataFrame()

    model  = joblib.load(SALES_MODEL_PATH)
    scaler = joblib.load(SALES_SCALER_PATH)

    # Use dummy features (scaled by average from training would be ideal;
    # for demo we increment month_num and keep others at median-ish)
    today_month = pd.Timestamp.now().year * 12 + pd.Timestamp.now().month
    rows = []
    for i in range(1, months_ahead + 1):
        m = today_month + i
        # Simple heuristic features for future months
        rows.append([m, 50000, 48000, 51000, 165, 520, 0.08])

    X = np.array(rows)
    X_s = scaler.transform(X)
    preds = model.predict(X_s)
    preds = np.maximum(preds, 0)

    future_dates = pd.date_range(
        start=pd.Timestamp.now() + pd.DateOffset(months=1),
        periods=months_ahead, freq="MS"
    )
    return pd.DataFrame({"month": future_dates, "predicted_revenue": preds.round(2)})


# ===========================================================================
# B. CUSTOMER CHURN PREDICTION  — Random Forest
# ===========================================================================

def prepare_churn_features(customers_df: pd.DataFrame,
                            orders_df: pd.DataFrame) -> pd.DataFrame:
    """Merge and engineer features for churn classification."""
    cust = customers_df.copy()
    cust["join_date"] = pd.to_datetime(cust["join_date"])

    # Days since joined
    cust["days_as_customer"] = (pd.Timestamp.now() - cust["join_date"]).dt.days

    # Encode categoricals
    le_region  = LabelEncoder()
    le_segment = LabelEncoder()
    cust["region_enc"]  = le_region.fit_transform(cust["region"].astype(str))
    cust["segment_enc"] = le_segment.fit_transform(cust["segment"].astype(str))

    # Order recency
    if orders_df is not None and len(orders_df) > 0:
        orders = orders_df.copy()
        orders["order_date"] = pd.to_datetime(orders["order_date"])
        last_order = orders.groupby("customer_id")["order_date"].max().reset_index()
        last_order.columns = ["customer_id", "last_order_date"]
        last_order["days_since_last_order"] = (
            pd.Timestamp.now() - last_order["last_order_date"]
        ).dt.days
        cust = cust.merge(last_order[["customer_id", "days_since_last_order"]],
                          on="customer_id", how="left")
    else:
        cust["days_since_last_order"] = 365

    cust["days_since_last_order"] = cust["days_since_last_order"].fillna(730)

    features = cust[[
        "total_purchases", "total_spent", "days_as_customer",
        "region_enc", "segment_enc", "days_since_last_order", "is_churned"
    ]].dropna()
    return features


def train_churn_model(customers_df: pd.DataFrame,
                       orders_df: pd.DataFrame) -> dict:
    """Train Random Forest for churn prediction. Returns metrics dict."""
    data = prepare_churn_features(customers_df, orders_df)
    if len(data) < 20:
        return {"error": "Not enough customer data."}

    feature_cols = ["total_purchases", "total_spent", "days_as_customer",
                    "region_enc", "segment_enc", "days_since_last_order"]
    X = data[feature_cols].values
    y = data["is_churned"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    model = RandomForestClassifier(n_estimators=150, random_state=42, n_jobs=-1)
    model.fit(X_train_s, y_train)

    y_pred = model.predict(X_test_s)
    metrics = {
        "Accuracy":  round(accuracy_score(y_test, y_pred), 4),
        "Report":    classification_report(y_test, y_pred, output_dict=True),
    }

    joblib.dump(model,  CHURN_MODEL_PATH)
    joblib.dump(scaler, CHURN_SCALER_PATH)
    return {"metrics": metrics, "feature_cols": feature_cols}


def predict_churn(input_data: dict) -> tuple:
    """
    Predict churn probability for a single customer.
    input_data keys: total_purchases, total_spent, days_as_customer,
                     region_enc, segment_enc, days_since_last_order
    Returns (prediction: int, probability: float)
    """
    if not CHURN_MODEL_PATH.exists():
        return None, None

    model  = joblib.load(CHURN_MODEL_PATH)
    scaler = joblib.load(CHURN_SCALER_PATH)

    feature_cols = ["total_purchases", "total_spent", "days_as_customer",
                    "region_enc", "segment_enc", "days_since_last_order"]
    X = np.array([[input_data.get(f, 0) for f in feature_cols]])
    X_s = scaler.transform(X)

    pred  = model.predict(X_s)[0]
    proba = model.predict_proba(X_s)[0][1]
    return int(pred), round(float(proba), 4)


# ===========================================================================
# C. CUSTOMER SEGMENTATION  — K-Means Clustering
# ===========================================================================

def prepare_segmentation_features(customers_df: pd.DataFrame,
                                   orders_df: pd.DataFrame = None) -> pd.DataFrame:
    """Build RFM-like features for clustering."""
    cust = customers_df.copy()
    cust["join_date"] = pd.to_datetime(cust["join_date"])
    cust["days_as_customer"] = (pd.Timestamp.now() - cust["join_date"]).dt.days

    if orders_df is not None and len(orders_df) > 0:
        orders = orders_df.copy()
        orders["order_date"] = pd.to_datetime(orders["order_date"])
        last_order = orders.groupby("customer_id")["order_date"].max().reset_index()
        last_order["recency"] = (pd.Timestamp.now() - last_order["order_date"]).dt.days
        cust = cust.merge(last_order[["customer_id", "recency"]], on="customer_id", how="left")
    else:
        cust["recency"] = 180

    cust["recency"] = cust["recency"].fillna(365)

    features = cust[["customer_id", "total_purchases", "total_spent",
                      "days_as_customer", "recency"]].dropna()
    return features


def train_segmentation_model(customers_df: pd.DataFrame,
                              orders_df: pd.DataFrame = None,
                              n_clusters: int = 4) -> dict:
    """Train K-Means clustering. Returns labeled DataFrame and inertia."""
    data = prepare_segmentation_features(customers_df, orders_df)
    if len(data) < n_clusters * 3:
        return {"error": "Not enough data for clustering."}

    feature_cols = ["total_purchases", "total_spent", "days_as_customer", "recency"]
    X = data[feature_cols].values

    scaler = StandardScaler()
    X_s = scaler.fit_transform(X)

    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10, max_iter=300)
    model.fit(X_s)

    data["cluster"] = model.labels_
    segment_labels = {0: "Champions", 1: "Loyal Customers",
                      2: "At Risk",   3: "New Customers"}
    data["segment_label"] = data["cluster"].map(
        lambda c: segment_labels.get(c, f"Segment {c}")
    )

    joblib.dump(model,  SEGMENT_MODEL_PATH)
    joblib.dump(scaler, SEGMENT_SCALER_PATH)

    return {
        "labeled_df":   data,
        "inertia":      round(model.inertia_, 2),
        "n_clusters":   n_clusters,
        "feature_cols": feature_cols,
    }


def load_model_if_exists(path: Path):
    """Safely load a joblib model, returns None if not found."""
    if path.exists():
        return joblib.load(path)
    return None


def models_trained() -> dict:
    """Return dict indicating which models are already trained."""
    return {
        "sales":       SALES_MODEL_PATH.exists(),
        "churn":       CHURN_MODEL_PATH.exists(),
        "segmentation": SEGMENT_MODEL_PATH.exists(),
    }
