-- =====================================================
-- BusinessVerse SQL Schema
-- Compatible with SQLite (default) and MySQL/PostgreSQL
-- =====================================================

-- 1. Customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id     TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    email           TEXT UNIQUE,
    region          TEXT,              -- North, South, East, West, Central
    segment         TEXT,              -- Consumer, Corporate, Home Office
    join_date       DATE,
    total_purchases INTEGER DEFAULT 0,
    total_spent     REAL DEFAULT 0.0,
    is_churned      INTEGER DEFAULT 0  -- 0 = Active, 1 = Churned
);

-- 2. Products table
CREATE TABLE IF NOT EXISTS products (
    product_id      TEXT PRIMARY KEY,
    product_name    TEXT NOT NULL,
    category        TEXT,              -- Technology, Furniture, etc.
    sub_category    TEXT,
    unit_price      REAL,
    cost_price      REAL
);

-- 3. Orders table
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

-- =====================================================
-- Sample Analytics Queries
-- =====================================================

-- Q1: Monthly Revenue & Profit
SELECT
    strftime('%Y-%m', order_date) AS month,
    SUM(revenue)                  AS total_revenue,
    SUM(profit)                   AS total_profit,
    COUNT(order_id)               AS total_orders
FROM orders
GROUP BY month
ORDER BY month;

-- Q2: Top 10 Products by Revenue
SELECT
    p.product_name,
    p.category,
    SUM(o.revenue)  AS total_revenue,
    SUM(o.quantity) AS units_sold,
    SUM(o.profit)   AS total_profit
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 10;

-- Q3: Region-wise Sales
SELECT
    region,
    SUM(revenue)  AS total_revenue,
    SUM(profit)   AS total_profit,
    COUNT(*)      AS total_orders
FROM orders
GROUP BY region
ORDER BY total_revenue DESC;

-- Q4: Customer Purchase Frequency
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

-- Q5: Best Performing Category & Sub-category
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

-- Q6: Category Profit Margins
SELECT
    p.category,
    SUM(o.revenue)  AS total_revenue,
    SUM(o.profit)   AS total_profit,
    COUNT(*)        AS total_orders,
    AVG(o.discount) AS avg_discount,
    ROUND(SUM(o.profit) * 100.0 / NULLIF(SUM(o.revenue), 0), 2) AS profit_margin_pct
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY profit_margin_pct DESC;
