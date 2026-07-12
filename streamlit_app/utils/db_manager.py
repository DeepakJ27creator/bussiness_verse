"""
BusinessVerse - Database Manager
Handles SQLAlchemy connection, schema creation, and SQL queries.
"""

import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

# ---------------------------------------------------------------------------
# Database path configuration
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "businessverse.db"
DATA_DIR = BASE_DIR / "data"

def get_engine():
    """Create and return a SQLAlchemy engine connected to the SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
    return engine


def init_database():
    """Initialize the database schema (customers, products, orders tables)."""
    engine = get_engine()
    sql_schema = """
    CREATE TABLE IF NOT EXISTS customers (
        customer_id     TEXT PRIMARY KEY,
        name            TEXT NOT NULL,
        email           TEXT UNIQUE,
        region          TEXT,
        segment         TEXT,
        join_date       DATE,
        total_purchases INTEGER DEFAULT 0,
        total_spent     REAL DEFAULT 0.0,
        is_churned      INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id      TEXT PRIMARY KEY,
        product_name    TEXT NOT NULL,
        category        TEXT,
        sub_category    TEXT,
        unit_price      REAL,
        cost_price      REAL
    );

    CREATE TABLE IF NOT EXISTS orders (
        order_id        TEXT PRIMARY KEY,
        customer_id     TEXT,
        product_id      TEXT,
        order_date      DATE,
        quantity        INTEGER,
        unit_price      REAL,
        discount        REAL DEFAULT 0.0,
        revenue         REAL,
        profit          REAL,
        region          TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id)  REFERENCES products(product_id)
    );
    """
    with engine.connect() as conn:
        for stmt in sql_schema.strip().split(";"):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()
    return engine


def load_data_to_db(customers_df: pd.DataFrame,
                     products_df: pd.DataFrame,
                     orders_df: pd.DataFrame):
    """Load DataFrames into the SQLite database, replacing existing data."""
    engine = get_engine()
    customers_df.to_sql("customers", engine, if_exists="replace", index=False)
    products_df.to_sql("products",  engine, if_exists="replace", index=False)
    orders_df.to_sql("orders",      engine, if_exists="replace", index=False)
    return True


def run_query(sql: str) -> pd.DataFrame:
    """Run any SELECT SQL query and return a DataFrame."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            return pd.read_sql_query(text(sql), conn)
    except Exception as e:
        return pd.DataFrame({"Error": [str(e)]})


# ---------------------------------------------------------------------------
# Pre-built analytics queries
# ---------------------------------------------------------------------------

def query_monthly_revenue() -> pd.DataFrame:
    sql = """
    SELECT
        strftime('%Y-%m', order_date) AS month,
        SUM(revenue)                  AS total_revenue,
        SUM(profit)                   AS total_profit,
        COUNT(order_id)               AS total_orders
    FROM orders
    GROUP BY month
    ORDER BY month;
    """
    return run_query(sql)


def query_top_products(limit: int = 10) -> pd.DataFrame:
    sql = f"""
    SELECT
        p.product_name,
        p.category,
        SUM(o.revenue)   AS total_revenue,
        SUM(o.quantity)  AS units_sold,
        SUM(o.profit)    AS total_profit
    FROM orders  o
    JOIN products p ON o.product_id = p.product_id
    GROUP BY p.product_name, p.category
    ORDER BY total_revenue DESC
    LIMIT {limit};
    """
    return run_query(sql)


def query_region_sales() -> pd.DataFrame:
    sql = """
    SELECT
        region,
        SUM(revenue)  AS total_revenue,
        SUM(profit)   AS total_profit,
        COUNT(*)      AS total_orders
    FROM orders
    GROUP BY region
    ORDER BY total_revenue DESC;
    """
    return run_query(sql)


def query_category_performance() -> pd.DataFrame:
    sql = """
    SELECT
        p.category,
        SUM(o.revenue)              AS total_revenue,
        SUM(o.profit)               AS total_profit,
        COUNT(o.order_id)           AS total_orders,
        AVG(o.discount)             AS avg_discount,
        ROUND(SUM(o.profit) * 100.0 / NULLIF(SUM(o.revenue), 0), 2) AS profit_margin_pct
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    GROUP BY p.category
    ORDER BY total_revenue DESC;
    """
    return run_query(sql)


def query_customer_purchase_frequency() -> pd.DataFrame:
    sql = """
    SELECT
        c.customer_id,
        c.name,
        c.segment,
        c.region,
        COUNT(o.order_id)  AS purchase_count,
        SUM(o.revenue)     AS total_spent,
        MAX(o.order_date)  AS last_purchase_date
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.name, c.segment, c.region
    ORDER BY total_spent DESC
    LIMIT 50;
    """
    return run_query(sql)


def query_best_performing_category() -> pd.DataFrame:
    sql = """
    SELECT
        p.category,
        p.sub_category,
        SUM(o.revenue) AS total_revenue,
        SUM(o.profit)  AS total_profit,
        COUNT(*)       AS orders
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    GROUP BY p.category, p.sub_category
    ORDER BY total_revenue DESC;
    """
    return run_query(sql)


def query_recent_transactions(limit: int = 20) -> pd.DataFrame:
    sql = f"""
    SELECT
        o.order_id,
        c.name         AS customer,
        p.product_name AS product,
        p.category,
        o.order_date,
        o.quantity,
        o.revenue,
        o.profit,
        o.region
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN products  p ON o.product_id  = p.product_id
    ORDER BY o.order_date DESC
    LIMIT {limit};
    """
    return run_query(sql)


def get_kpis() -> dict:
    """Return aggregated KPI values for the dashboard."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            revenue   = conn.execute(text("SELECT COALESCE(SUM(revenue), 0) FROM orders")).scalar()
            profit    = conn.execute(text("SELECT COALESCE(SUM(profit), 0) FROM orders")).scalar()
            orders    = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar()
            customers = conn.execute(text("SELECT COUNT(*) FROM customers")).scalar()
        return {
            "total_revenue":   round(revenue,   2),
            "total_profit":    round(profit,    2),
            "total_orders":    int(orders),
            "total_customers": int(customers),
        }
    except Exception:
        return {"total_revenue": 0, "total_profit": 0, "total_orders": 0, "total_customers": 0}
