"""
BusinessVerse - Sample Data Generator
Generates realistic customers, products, and orders datasets
and loads them into the SQLite database.

Run directly:  python streamlit_app/utils/data_generator.py
"""

import random
import string
import numpy as np
import pandas as pd
from faker import Faker
from pathlib import Path
import sys

# Make sure imports resolve when run as script
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from streamlit_app.utils.db_manager import load_data_to_db, init_database, DATA_DIR

fake = Faker()
random.seed(42)
np.random.seed(42)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REGIONS = ["North", "South", "East", "West", "Central"]
SEGMENTS = ["Consumer", "Corporate", "Home Office"]

CATEGORIES = {
    "Technology":  ["Phones", "Computers", "Accessories", "Cameras"],
    "Furniture":   ["Chairs", "Tables", "Bookcases", "Furnishings"],
    "Office Supplies": ["Paper", "Binders", "Art Supplies", "Labels", "Storage"],
    "Clothing":    ["Shirts", "Pants", "Outerwear", "Footwear"],
    "Food & Beverage": ["Snacks", "Beverages", "Bakery", "Dairy"],
}

PRODUCT_PRICE_RANGES = {
    "Technology":      (50,  2500),
    "Furniture":       (30,  1800),
    "Office Supplies": (5,   200),
    "Clothing":        (15,  350),
    "Food & Beverage": (2,   80),
}


def gen_id(prefix: str, n: int = 6) -> str:
    return prefix + ''.join(random.choices(string.digits, k=n))


# ---------------------------------------------------------------------------
# Generate Customers
# ---------------------------------------------------------------------------
def generate_customers(n: int = 500) -> pd.DataFrame:
    records = []
    for _ in range(n):
        cid = gen_id("CUST-")
        join = fake.date_between(start_date="-4y", end_date="-1m")
        records.append({
            "customer_id":     cid,
            "name":            fake.name(),
            "email":           fake.email(),
            "region":          random.choice(REGIONS),
            "segment":         random.choice(SEGMENTS),
            "join_date":       join,
            "total_purchases": 0,      # filled after orders
            "total_spent":     0.0,    # filled after orders
            "is_churned":      int(random.random() < 0.25),  # 25% churn rate
        })
    return pd.DataFrame(records).drop_duplicates(subset=["customer_id"])


# ---------------------------------------------------------------------------
# Generate Products
# ---------------------------------------------------------------------------
def generate_products(n: int = 120) -> pd.DataFrame:
    records = []
    ids_used = set()
    for _ in range(n):
        pid = gen_id("PROD-")
        while pid in ids_used:
            pid = gen_id("PROD-")
        ids_used.add(pid)

        cat = random.choice(list(CATEGORIES.keys()))
        subcat = random.choice(CATEGORIES[cat])
        lo, hi = PRODUCT_PRICE_RANGES[cat]
        unit_price = round(random.uniform(lo, hi), 2)
        cost_price = round(unit_price * random.uniform(0.45, 0.72), 2)

        records.append({
            "product_id":   pid,
            "product_name": f"{fake.word().capitalize()} {subcat} {fake.word().capitalize()}",
            "category":     cat,
            "sub_category": subcat,
            "unit_price":   unit_price,
            "cost_price":   cost_price,
        })
    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Generate Orders
# ---------------------------------------------------------------------------
def generate_orders(customers: pd.DataFrame, products: pd.DataFrame,
                    n: int = 5000) -> pd.DataFrame:
    cust_ids = customers["customer_id"].tolist()
    prod_ids = products["product_id"].tolist()

    prod_lookup = products.set_index("product_id")[["unit_price", "cost_price", "category"]].to_dict("index")

    records = []
    order_ids_used = set()

    for _ in range(n):
        oid = gen_id("ORD-", 8)
        while oid in order_ids_used:
            oid = gen_id("ORD-", 8)
        order_ids_used.add(oid)

        cid = random.choice(cust_ids)
        pid = random.choice(prod_ids)
        qty = random.randint(1, 15)
        discount = round(random.choice([0, 0, 0, 0.05, 0.10, 0.15, 0.20, 0.30]), 2)
        unit_price = prod_lookup[pid]["unit_price"]
        cost_price = prod_lookup[pid]["cost_price"]

        revenue = round(unit_price * qty * (1 - discount), 2)
        profit  = round((unit_price - cost_price) * qty * (1 - discount), 2)

        # Weighted date distribution: more recent orders have slightly higher frequency
        order_date = fake.date_between(start_date="-3y", end_date="today")

        # Assign region from customer or random
        cust_region = customers.loc[customers["customer_id"] == cid, "region"].values
        region = cust_region[0] if len(cust_region) > 0 else random.choice(REGIONS)

        records.append({
            "order_id":   oid,
            "customer_id": cid,
            "product_id":  pid,
            "order_date":  order_date,
            "quantity":    qty,
            "unit_price":  unit_price,
            "discount":    discount,
            "revenue":     revenue,
            "profit":      profit,
            "region":      region,
        })

    orders_df = pd.DataFrame(records).sort_values("order_date").reset_index(drop=True)
    return orders_df


# ---------------------------------------------------------------------------
# Update customer aggregates
# ---------------------------------------------------------------------------
def update_customer_aggregates(customers: pd.DataFrame,
                                orders: pd.DataFrame) -> pd.DataFrame:
    agg = orders.groupby("customer_id").agg(
        total_purchases=("order_id", "count"),
        total_spent=("revenue", "sum")
    ).reset_index()
    customers = customers.merge(agg, on="customer_id", how="left", suffixes=("_old", ""))
    customers["total_purchases"] = customers["total_purchases"].fillna(0).astype(int)
    customers["total_spent"]     = customers["total_spent"].fillna(0).round(2)
    # drop old columns if they exist
    for col in ["total_purchases_old", "total_spent_old"]:
        if col in customers.columns:
            customers.drop(columns=[col], inplace=True)
    return customers


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def generate_and_save(save_csv: bool = True) -> tuple:
    """Generate all datasets, save to CSV and SQLite, return DataFrames."""
    print("[*] Generating customers...")
    customers = generate_customers(500)

    print("[*] Generating products...")
    products = generate_products(120)

    print("[*] Generating orders...")
    orders = generate_orders(customers, products, 5000)

    print("[*] Updating customer aggregates...")
    customers = update_customer_aggregates(customers, orders)

    if save_csv:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        customers.to_csv(DATA_DIR / "customers.csv", index=False)
        products.to_csv( DATA_DIR / "products.csv",  index=False)
        orders.to_csv(   DATA_DIR / "orders.csv",    index=False)
        print(f"[OK] CSVs saved to: {DATA_DIR}")

    print("[*] Initializing database...")
    init_database()

    print("[*] Loading data into SQLite database...")
    load_data_to_db(customers, products, orders)
    print("[OK] Database populated successfully!")

    return customers, products, orders


if __name__ == "__main__":
    generate_and_save()
    print("\n[DONE] Sample data generation complete.")
