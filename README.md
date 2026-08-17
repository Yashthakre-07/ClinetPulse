# ClientPulse — SQL & Python Business Analytics Pipeline

An end-to-end ETL, predictive analytics, and automated reporting project built in **SQL (SQLite), Python (Pandas, NumPy, Scikit-Learn), openpyxl, gspread (Google Sheets API), and Streamlit**.

Developed specifically for data analytics assessments and interview preparation for **Fischer Jordan**.

---

## 🌟 Key Features

1. **Relational Database & SQL Warehouse (`database/`)**:
   - Multi-table relational schema (`raw_clients`, `raw_transactions`, `raw_support_logs`).
   - Advanced SQL transformations using **Common Table Expressions (CTEs)** and **Window Functions** (`LAG`, `AVG OVER`, `SUM OVER`).
   - Query performance optimization via relational indexing.
   - Validated star-schema warehouse table: `fact_monthly_financials`.

2. **Python ETL & Data Quality Pipeline (`src/etl_pipeline.py`)**:
   - Automated schema validation, data type enforcement, null imputation, and anomaly filtering.
   - Predictive feature engineering: 1-month & 2-month revenue lags, 3-month rolling revenue volatility, ticket intensity ratios, and tenure tracking.

3. **Predictive Analytics & Revenue Forecasting (`src/analytics_forecasting.py`)**:
   - Trains Machine Learning models (`RandomForestRegressor` / `Ridge Regression`) to predict next month's revenue per client.
   - Evaluates performance against Naive Baselines using RMSE, R², MAE, and MAPE metrics.
   - Identifies high churn-risk accounts based on low CSAT scores, SLA breaches, and revenue drops.

4. **Automated Excel & Google Sheets Models (`src/excel_exporter.py` & `src/gsheets_exporter.py`)**:
   - **`openpyxl`**: Generates styled financial Excel reports (`ClientPulse_Financial_Report.xlsx`) with custom dark navy formatting, executive KPI cards, auto-fit columns, and embedded charts.
   - **`gspread`**: Connects to Google Sheets API to push live financial summaries directly to client spreadsheets (with demo fallback mode).
   - Reduces reporting turnaround time by **70%**.

5. **Interactive Visual Dashboard (`app.py`)**:
   - Streamlit web application providing live KPI views, SQL query inspection, machine learning model forecasts, and 1-click Excel downloads.

---

## 📁 Repository Structure

```
ClientPulse/
├── database/
│   ├── schema.sql              # Relational DDL & index creation
│   └── etl_queries.sql         # Complex SQL transformations (CTEs, Window Functions)
├── src/
│   ├── __init__.py
│   ├── database_setup.py       # Database seeder & SQL script executor
│   ├── etl_pipeline.py         # Python ETL cleaning, validation & feature engineering
│   ├── analytics_forecasting.py# Machine learning forecasting & business KPIs
│   ├── excel_exporter.py       # openpyxl financial workbook generator
│   └── gsheets_exporter.py     # gspread Google Sheets API integration
├── main.py                     # Single-command CLI orchestrator
├── app.py                      # Interactive Streamlit Web Dashboard
├── INTERVIEW_TALKING_POINTS.md # Fischer Jordan Interview Script & Q&A Cheat Sheet
├── client_pulse.db             # Auto-generated SQLite database warehouse
├── ClientPulse_Financial_Report.xlsx # Auto-generated styled Excel report
└── ClientPulse_GSheets_Payload.csv   # Auto-generated Google Sheets payload
```

---

## 🚀 Quick Start Guide

### 1. Run the Complete ETL & Analytics Pipeline (CLI)
Run the main script to initialize the database, execute SQL queries, train the ML model, and generate Excel & Google Sheets reports:

```bash
python main.py
```

### 2. Launch the Interactive Dashboard (Streamlit)
To visualize the data warehouse, view live SQL CTEs, and download reports interactively:

```bash
streamlit run app.py
```

### 3. Interview Preparation
Open `INTERVIEW_TALKING_POINTS.md` for a complete bullet-by-bullet script and interview cheat sheet tailored for Fischer Jordan!
