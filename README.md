<div align="center">

# 📊 BusinessVerse

### End-to-End Business Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3%2B-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-D71F00?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

**A production-grade business analytics dashboard** combining SQL databases, interactive Plotly charts, and machine learning models — all inside a clean, professional Streamlit UI.

[🚀 Features](#-features) · [📸 Screenshots](#-screenshots) · [🛠 Tech Stack](#-tech-stack) · [⚡ Quick Start](#-quick-start) · [📁 Project Structure](#-project-structure) · [🤖 ML Models](#-machine-learning-models) · [🗄 SQL Schema](#-sql-schema)

</div>

---

## 📸 Screenshots

<table>
  <tr>
    <td><b>🔐 Login</b></td>
    <td><b>🏠 Dashboard — KPI Cards & Charts</b></td>
  </tr>
  <tr>
    <td>Clean, centered login form</td>
    <td>$15M revenue, 5K orders, interactive Plotly charts</td>
  </tr>
  <tr>
    <td><b>📈 Business Analytics</b></td>
    <td><b>🤖 Machine Learning</b></td>
  </tr>
  <tr>
    <td>5-tab analysis with date/region/category filters</td>
    <td>Sales prediction gauge + customer segmentation clusters</td>
  </tr>
</table>

---

## 🌟 Features

### 🔐 Authentication System
- Simple session-based login / logout
- Sidebar navigation with user status indicator
- Demo credentials provided (`demo / demo`)

### 🏠 Dashboard
- **4 KPI Cards** — Revenue, Orders, Customers, Profit
- **Monthly Revenue & Profit Trend** — area + line chart
- **Region-wise Revenue** — donut chart
- **Top 10 Products by Revenue** — horizontal bar chart
- **Category Performance** — vertical bar chart
- **Monthly Order Volume** — bar chart
- **Recent Transactions** — sortable data table

### 📁 Data Upload
- Upload any CSV file
- Auto-detect column types and statistics
- Tabs: Preview · Statistics · Missing Values · Column Info
- Load built-in sample dataset with one click

### 🧹 Data Cleaning
- Drop rows with null values
- Fill missing values (Mean / Median / Mode / Zero / Custom)
- Remove duplicate rows
- Convert column data types (int, float, str, datetime)
- Drop selected columns (feature selection)
- Download cleaned dataset as CSV

### 🗄️ SQL Analytics
- **Monthly Revenue & Profit** — grouped bar chart
- **Top Products by Revenue** — colored horizontal bar
- **Region-wise Sales** — bar + pie chart combo
- **Category & Sub-category Performance** — treemap
- **Customer Purchase Frequency** — scatter plot
- **Custom SQL Editor** — run any SELECT query live

### 📈 Business Analytics (with Filters)
**Sidebar Filters:** Date range · Region · Category · Customer Segment

| Tab | Content |
|---|---|
| Sales Trends | Monthly area chart, regional bars, segment donut, avg order value |
| Profit Analysis | Category revenue vs profit grouped bar, margin % bar, discount scatter |
| Customer Analysis | Segment orders bar, segment×region heatmap |
| Product Analysis | Sub-category treemap, revenue vs orders scatter |
| Time Series | Weekly trend, day-of-week revenue, day-of-month revenue |

### 🤖 Machine Learning
| Model | Algorithm | Target | Metrics |
|---|---|---|---|
| Sales Prediction | Linear Regression | Monthly Revenue | MAE, RMSE, R² |
| Churn Prediction | Random Forest | Customer Churn (0/1) | Accuracy, Precision, Recall |
| Customer Segmentation | K-Means | Customer Clusters | Inertia |

- Train with one click from the UI
- Models saved to `models/` using **joblib**
- Live **gauge meter** for churn probability
- Configurable K (2–8 segments) for clustering

### 📄 Reports & Export
- Download **cleaned dataset** as CSV or Excel
- Download individual analytics reports as CSVs
- **Full Excel bundle** — all reports in one multi-sheet workbook
- Download trained ML models (`.pkl` files)

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend & UI | Streamlit 1.28+ |
| Charts | Plotly Express + Graph Objects |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn (LinearRegression, RandomForestClassifier, KMeans) |
| Model Persistence | Joblib |
| Database ORM | SQLAlchemy 2.0 |
| Database | SQLite (switchable to MySQL / PostgreSQL) |
| Sample Data | Faker |
| Export | OpenPyXL (Excel) |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.9 or higher
- pip

### 1. Clone the repository
```bash
git clone https://github.com/DeepakJ27creator/bussiness_verse.git
cd bussiness_verse
```


### 2. Create virtual environment (recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Generate sample data & database
```bash
python streamlit_app/utils/data_generator.py
```
This creates:
- `data/customers.csv` — 500 realistic customers
- `data/products.csv` — 120 products across 5 categories  
- `data/orders.csv` — 5,000 orders over 3 years
- `data/businessverse.db` — SQLite database

### 5. Run the application
```bash
streamlit run streamlit_app/app.py
```

### 6. Open in browser
```
http://localhost:8501
```

### Demo Credentials
| Username | Password |
|---|---|
| `demo` | `demo` |
| `admin` | `admin123` |
| `analyst` | `analyst123` |

---

## 📁 Project Structure

```
BusinessVerse/
│
├── .streamlit/
│   └── config.toml              # Light theme + server config
│
├── data/                        # Auto-generated sample datasets
│   ├── customers.csv            # 500 customers
│   ├── products.csv             # 120 products
│   ├── orders.csv               # 5,000 orders
│   └── businessverse.db         # SQLite database (gitignored)
│
├── models/                      # Trained ML model files (gitignored)
│   ├── sales_model.pkl
│   ├── sales_scaler.pkl
│   ├── churn_model.pkl
│   ├── churn_scaler.pkl
│   ├── segment_model.pkl
│   └── segment_scaler.pkl
│
├── sql/
│   └── schema.sql               # DB schema + 6 analytics queries
│
├── notebooks/                   # Jupyter exploration notebooks
│
├── streamlit_app/
│   ├── app.py                   # Entry point — auth + navigation
│   │
│   ├── assets/
│   │   └── style.css            # Custom professional CSS
│   │
│   ├── pages/
│   │   ├── 1_Dashboard.py       # KPI cards + 7 Plotly charts
│   │   ├── 2_Data_Upload.py     # CSV upload + 4 analysis tabs
│   │   ├── 3_Data_Cleaning.py   # 6 cleaning operations
│   │   ├── 4_SQL_Analytics.py   # 5 pre-built queries + SQL editor
│   │   ├── 5_Business_Analytics.py # 5-tab analytics + sidebar filters
│   │   ├── 6_Machine_Learning.py   # 3 ML models with live UI
│   │   └── 7_Report_Generation.py  # CSV/Excel/model exports
│   │
│   └── utils/
│       ├── __init__.py
│       ├── db_manager.py        # SQLAlchemy + 7 analytics queries
│       ├── data_generator.py    # Faker-based sample data generator
│       └── ml_utils.py          # Train/predict: LR + RF + KMeans
│
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🤖 Machine Learning Models

### A. Sales Prediction — Linear Regression
**Features used:**
- Month number (ordinal)
- Lag-1 and Lag-2 monthly revenue
- 3-month rolling mean
- Total orders and quantity
- Average discount

**Output:** Predicted total revenue for next 1–24 months  
**Evaluation metrics:** MAE, RMSE, R² on 20% holdout set

### B. Customer Churn Prediction — Random Forest (150 trees)
**Features used:**
- Total purchases and total spent
- Days as customer
- Days since last order (recency)
- Region and segment (encoded)

**Output:** Churn probability (0–100%) with risk level classification  
**Evaluation:** Accuracy + full classification report

### C. Customer Segmentation — K-Means (configurable K)
**Features used:** RFM-style  
- Total purchases (Frequency)
- Total spent (Monetary)
- Days since last order (Recency)
- Days as customer (Tenure)

**Output:** Customer segment labels (Champions, Loyal, At Risk, New Customers) with scatter visualization

---

## 🗄 SQL Schema

```sql
CREATE TABLE customers (
    customer_id     TEXT PRIMARY KEY,
    name            TEXT,
    email           TEXT UNIQUE,
    region          TEXT,      -- North/South/East/West/Central
    segment         TEXT,      -- Consumer/Corporate/Home Office
    join_date       DATE,
    total_purchases INTEGER,
    total_spent     REAL,
    is_churned      INTEGER    -- 0=Active, 1=Churned
);

CREATE TABLE products (
    product_id      TEXT PRIMARY KEY,
    product_name    TEXT,
    category        TEXT,
    sub_category    TEXT,
    unit_price      REAL,
    cost_price      REAL
);

CREATE TABLE orders (
    order_id        TEXT PRIMARY KEY,
    customer_id     TEXT REFERENCES customers,
    product_id      TEXT REFERENCES products,
    order_date      DATE,
    quantity        INTEGER,
    unit_price      REAL,
    discount        REAL,
    revenue         REAL,
    profit          REAL,
    region          TEXT
);
```

> See [`sql/schema.sql`](sql/schema.sql) for the full schema + 6 pre-built analytics queries.

---

## 🔧 Switching to MySQL / PostgreSQL

Change the connection string in `streamlit_app/utils/db_manager.py`:

```python
# MySQL (requires: pip install pymysql)
engine = create_engine("mysql+pymysql://user:password@localhost/businessverse")

# PostgreSQL (requires: pip install psycopg2-binary)
engine = create_engine("postgresql://user:password@localhost/businessverse")
```

Then run `init_database()` once to create the schema on your server.

---

## 🔮 Future Improvements

- [ ] Role-based access control (RBAC)
- [ ] Real-time data streaming (Kafka / WebSocket)
- [ ] Email report scheduling (cron + SMTP)
- [ ] Advanced forecasting (Prophet, ARIMA, LSTM)
- [ ] Customer Lifetime Value (CLV) scoring
- [ ] A/B testing analytics module
- [ ] REST API layer (FastAPI) for headless access
- [ ] Docker containerization & Docker Compose setup
- [ ] Cloud deployment guide (Streamlit Cloud, AWS, GCP, Azure)
- [ ] Multi-tenant workspace support

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Deepak J** — [@DeepakJ27creator](https://github.com/DeepakJ27creator)

---

<div align="center">
  <p>Built with ❤️ using Python & Streamlit</p>
  <p>⭐ Star this repo if you found it useful!</p>
</div>
