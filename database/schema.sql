-- ClientPulse: Relational Database Schema (SQLite compatible)

DROP TABLE IF EXISTS raw_transactions;
DROP TABLE IF EXISTS raw_support_logs;
DROP TABLE IF EXISTS raw_clients;
DROP TABLE IF EXISTS fact_monthly_financials;
DROP TABLE IF EXISTS dim_clients;

-- 1. Raw Client Metadata Table
CREATE TABLE raw_clients (
    client_id VARCHAR(10) PRIMARY KEY,
    client_name VARCHAR(100) NOT NULL,
    industry VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    onboard_date DATE NOT NULL,
    contract_tier VARCHAR(20) NOT NULL -- 'Enterprise', 'Mid-Market', 'SMB'
);

-- 2. Raw Transactions Table (Relational Source 1)
CREATE TABLE raw_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id VARCHAR(10) NOT NULL,
    transaction_date DATE NOT NULL,
    monthly_fee REAL NOT NULL,
    operational_cost REAL NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'Paid',
    FOREIGN KEY (client_id) REFERENCES raw_clients(client_id)
);

-- 3. Raw Support & Satisfaction Logs (Relational Source 2)
CREATE TABLE raw_support_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id VARCHAR(10) NOT NULL,
    log_date DATE NOT NULL,
    tickets_opened INTEGER DEFAULT 0,
    sla_met_flag INTEGER DEFAULT 1, -- 1 = Yes, 0 = No
    csat_score REAL CHECK (csat_score >= 1.0 AND csat_score <= 5.0),
    FOREIGN KEY (client_id) REFERENCES raw_clients(client_id)
);

-- Performance Indexes (Optimizing Join and Aggregation queries)
CREATE INDEX idx_trans_client_date ON raw_transactions(client_id, transaction_date);
CREATE INDEX idx_support_client_date ON raw_support_logs(client_id, log_date);
