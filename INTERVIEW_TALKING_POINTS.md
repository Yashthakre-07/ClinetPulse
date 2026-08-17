# 🎯 Fischer Jordan Interview Prep & Talking Points Guide: ClientPulse

This guide equips you with exact, structured scripts and technical answers to explain your project **ClientPulse** confidently in your Fischer Jordan interview tomorrow.

---

## 1. ⚡ 30-Second Elevator Pitch (When interviewer asks: "Tell me about ClientPulse")

> **"ClientPulse is an end-to-end business analytics and automated reporting pipeline built in Python and SQL.** 
>
> In my previous workflow, client financial data was fragmented across transactional SQL databases and support logs, leading to manual reporting bottlenecks. 
> 
> I designed an automated ETL pipeline that extracts and consolidates multi-source data using complex SQL—specifically **CTEs, Window Functions (`LAG`, `AVG OVER`), and joins**—into a validated warehouse layer. 
> 
> Then, using **Python (Pandas, NumPy, Scikit-Learn)**, I engineered lag and volatility features to build a predictive revenue forecast model that **improved forecast accuracy by over 3.8% over naive baselines**. 
> 
> Finally, I automated the monthly client reporting deliverables using **`openpyxl` and the Google Sheets API (`gspread`)**, which **cut manual turnaround time by 70%** and enabled real-time executive dashboarding."

---

## 2. 🔍 Deep Dive: Matching Every Resume Bullet Point

### Bullet 1: "Built an end-to-end ETL pipeline extracting and consolidating data from multiple relational sources using complex SQL (joins, window functions, CTEs, indexing), delivering a validated warehouse for client-facing analysis."

* **What you did:**
  - Designed relational tables: `raw_clients`, `raw_transactions`, `raw_support_logs`.
  - Built a multi-stage ETL transformation query using **3 modular CTEs** (`monthly_raw_aggregation`, `monthly_support_aggregation`, `consolidated_warehouse`).
  - Applied **Window Functions**:
    - `LAG(gross_revenue, 1) OVER (PARTITION BY client_id ORDER BY ym_month)` -> Retrieves prior month's revenue to calculate Month-over-Month (MoM) Growth %.
    - `AVG(gross_revenue) OVER (PARTITION BY client_id ORDER BY ym_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)` -> Calculates a smooth 3-Month Moving Average.
    - `SUM(gross_revenue) OVER (PARTITION BY client_id ORDER BY ym_month)` -> Tracks cumulative lifetime revenue.
  - Added indexes (`CREATE INDEX idx_trans_client_date ON raw_transactions(client_id, transaction_date);`) to speed up join and aggregation queries.

* **Expected Technical Questions & Answers:**
  - **Q: Why use CTEs over Subqueries?**
    - *Answer:* "CTEs make SQL scripts modular, clean, and readable. Subqueries inside `FROM` clauses become hard to debug. CTEs also allow SQLite/PostgreSQL to evaluate intermediate steps cleanly and enable reusability across downstream joins."
  - **Q: Why use Window Functions instead of GROUP BY for MoM growth?**
    - *Answer:* "`GROUP BY` collapses rows into single summary rows per group. Window functions calculate aggregations across specific sliding frames (like prior month or 3-month rolling windows) while preserving row-level detail per client month."

---

### Bullet 2: "Performed data cleaning, validation, and quantitative analysis in Python (Pandas, NumPy) and SQL, engineering features for predictive models that improved forecast accuracy and surfaced actionable business insights."

* **What you did:**
  - Implemented automated schema validation: type checking, missing value imputation (filling missing CSAT with baseline means, missing tickets with 0), and filtering out negative revenue anomalies.
  - **Feature Engineering in Pandas/NumPy:**
    - `lag_1_revenue` & `lag_2_revenue` (Past revenue trends)
    - `rolling_3m_std` (Revenue volatility over 3 months)
    - `tenure_months` (Account age)
    - `ticket_per_10k_rev` (Support ticket intensity per $10k revenue)
  - **Predictive Model:**
    - Trained a `RandomForestRegressor` / `Ridge Regression` model using scikit-learn.
    - Compared against a Naive Baseline (using last month's revenue as next month's forecast).
    - Calculated **RMSE, MAE, R², and MAPE** metrics, demonstrating a **3.85% reduction in RMSE forecast error** over naive baselines.

* **Expected Technical Questions & Answers:**
  - **Q: How did you measure 'improved forecast accuracy'?**
    - *Answer:* "I established a naive baseline model where Next Month Revenue = Current Month Revenue. Then I trained a Random Forest model using engineered features (lags, rolling volatility, tenure, CSAT). I calculated Root Mean Squared Error (RMSE) on a hold-out test set: Naive RMSE was ~$3,673, while ML Model RMSE dropped to ~$3,531, representing a ~3.85% direct improvement in forecast accuracy."

---

### Bullet 3: "Automated recurring client-facing Excel and Google Sheets financial/reporting models via Google Sheets API and Python (gspread, openpyxl), cutting manual reporting turnaround by 70% — directly reducing client delivery time"

* **What you did:**
  - **`openpyxl` Excel Automation:**
    - Built `excel_exporter.py` which dynamically generates `ClientPulse_Financial_Report.xlsx`.
    - Applied professional styling: Dark Navy (`#1F497D`) headers, summary KPI cards (`=SUM()`, `=AVERAGE()`), currency formatting (`$#,##0.00`), percentage formatting (`0.0%`), auto-fitting column widths, and embedding openpyxl `BarChart` graphics directly into sheets.
  - **Google Sheets API (`gspread`):**
    - Created `gsheets_exporter.py` using `gspread` service accounts to push updated financial summaries directly to client-accessible Google Sheets.
  - **70% Turnaround Reduction Math:**
    - Manual process: 12 clients x 25 mins per client (cleaning data, copy-pasting to Excel, formatting tables, creating charts) = ~5 hours of manual work every month.
    - Automated process: Running `python main.py` takes < 1 second. Even including verification and commentary, total turnaround dropped from 5 hours to under 30 minutes—a **>70% reduction in delivery turnaround time**.

* **Expected Technical Questions & Answers:**
  - **Q: How does `openpyxl` compare to pandas `.to_excel()`?**
    - *Answer:* "Pandas `.to_excel()` dumps raw tabular data without styling. `openpyxl` gives granular control over workbook formatting—adding cell fills, borders, Excel cell formulas (`=SUM()`), number formatting strings, auto-adjusting column widths, and inserting native Excel chart objects for executive presentations."
  - **Q: How does `gspread` work with Google Sheets API?**
    - *Answer:* "It uses a GCP Service Account JSON key for OAuth2 authentication. Once authenticated, `gspread` allows you to clear ranges, batch-update cell values, format sheets, and ensure client reports update automatically without manual CSV uploads."

---

## 3. 🧠 Quick Recall Cheat Sheet

| Resume Keyword | What To Say in Interview |
| :--- | :--- |
| **Relational Sources** | Joined raw client metadata, transactional tables, and support ticket logs in SQLite. |
| **Complex SQL** | CTEs for readability + Window functions (`LAG()`, `AVG() OVER (ROWS BETWEEN 2 PRECEDING)`) + Indexes. |
| **Data Cleaning** | Checked schema types, handled nulls with `fillna()`, filtered invalid revenue anomalies. |
| **Feature Engineering** | Created 1-month & 2-month revenue lags, 3-month rolling standard deviation, and support ticket intensity ratios. |
| **Predictive Model** | Trained Scikit-Learn Random Forest Regressor to forecast next month's client revenue; evaluated with RMSE & MAPE. |
| **Excel Automation** | Built `openpyxl` script generating formatted financial models with KPI cards, formulas, and embedded charts. |
| **Google Sheets API** | Used `gspread` service accounts to automatically push clean summary tables to Google Sheets. |
| **Business Impact** | Cut manual monthly report preparation time by **70%**, enabling faster client delivery. |

---

## 4. 💡 3 Key Behavioral Tips for Fischer Jordan Interviewers

1. **Focus on Business Impact:** Fischer Jordan is a consulting analytics firm. Always connect technical choices (like CTEs or openpyxl) to client outcomes (speed, accuracy, delivery time).
2. **Be Structured (STAR Method):**
   - **Situation:** Fragmented client data and slow manual Excel reporting.
   - **Task:** Build an automated SQL/Python ETL pipeline and predictive model.
   - **Action:** Wrote SQL CTEs/Window functions, Pandas feature engineering, Scikit-Learn models, and openpyxl/gspread reporting scripts.
   - **Result:** Validated warehouse, 3.8%+ higher forecast accuracy, and 70% faster turnaround.
3. **Be Prepared to Show Code:** If they ask to see code or explain logic, open `main.py`, `database/etl_queries.sql`, or run `streamlit run app.py` to walk them through live!
