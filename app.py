import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

from src.database_setup import DB_PATH, SCHEMA_SQL, ETL_SQL, init_db
from src.etl_pipeline import run_etl
from src.analytics_forecasting import run_analytics
from src.excel_exporter import generate_styled_excel_report, OUTPUT_EXCEL
from src.gsheets_exporter import sync_to_gsheets

st.set_page_config(
    page_title="ClientPulse — Business Analytics Dashboard",
    page_icon="📈",
    layout="wide"
)

# Title Header
st.title("📈 ClientPulse — SQL & Python Business Analytics Dashboard")
st.caption("End-to-End ETL Pipeline, SQL Warehouse, Predictive Revenue Forecasting & Financial Model Automation")

# Sidebar Controls
st.sidebar.header("⚙️ Pipeline Controls")
if st.sidebar.button("🔄 Run Pipeline End-to-End"):
    init_db()
    run_etl()
    generate_styled_excel_report()
    sync_to_gsheets()
    st.sidebar.success("Pipeline executed successfully!")

st.sidebar.markdown("---")
st.sidebar.markdown("### 💼 Fischer Jordan Resume Project")
st.sidebar.info(
    "**Tech Stack:**\n"
    "- **Database:** SQLite (CTEs, Window Functions, Joins, Indexes)\n"
    "- **Data Science:** Python, Pandas, NumPy, Scikit-Learn\n"
    "- **Automation:** openpyxl, gspread (Google Sheets API)\n"
    "- **UI/Visualization:** Streamlit, Plotly"
)

# Load Warehouse Data
@st.cache_data(ttl=5)
def get_warehouse_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM fact_monthly_financials ORDER BY ym_month, gross_revenue DESC;", conn)
    conn.close()
    return df

try:
    df_wh = get_warehouse_data()
except Exception:
    init_db()
    run_etl()
    df_wh = get_warehouse_data()

# Compute KPIs
kpis, forecast_df, metrics, insights = run_analytics()

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive KPI Overview", 
    "🗄️ SQL Warehouse & CTE Inspector", 
    "🤖 ML Revenue Forecast & Churn Risk", 
    "📄 Automated Excel & GSheets Reports"
])

# TAB 1: EXECUTIVE OVERVIEW
with tab1:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Monthly Revenue", f"${kpis['total_monthly_revenue']:,.2f}")
    col2.metric("Annual Run Rate (ARR)", f"${kpis['annual_run_rate_arr']:,.2f}")
    col3.metric("Avg Account Rev (ARPU)", f"${kpis['arpu']:,.2f}")
    col4.metric("Avg Profit Margin", f"{kpis['avg_profit_margin_pct']}%")
    col5.metric("Churn Risk Accounts", f"{kpis['churn_risk_clients']}", delta="-Risk Alert" if kpis['churn_risk_clients'] > 0 else "Optimal", delta_color="inverse")

    st.markdown("---")
    
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Monthly Portfolio Revenue Trend")
        monthly_trend = df_wh.groupby('ym_month')['gross_revenue'].sum().reset_index()
        fig_trend = px.line(monthly_trend, x='ym_month', y='gross_revenue', title="Portfolio Revenue Over Time ($)", markers=True, line_shape="spline")
        fig_trend.update_layout(xaxis_title="Month", yaxis_title="Revenue ($)")
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_right:
        st.subheader("Revenue by Client Industry")
        latest_month = df_wh['ym_month'].max()
        latest_df = df_wh[df_wh['ym_month'] == latest_month]
        fig_pie = px.pie(latest_df, names='industry', values='gross_revenue', hole=0.4, title=f"Revenue Mix ({latest_month})")
        st.plotly_chart(fig_pie, use_container_width=True)

# TAB 2: SQL WAREHOUSE INSPECTOR
with tab2:
    st.subheader("🗄️ Validated Warehouse Fact Table (`fact_monthly_financials`)")
    st.dataframe(df_wh, use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 SQL ETL Transformation Queries (`database/etl_queries.sql`)")
    st.info("Demonstrating Common Table Expressions (CTEs), Window Functions (`LAG`, `AVG OVER`, `SUM OVER`), Multi-Table Joins, and Indexing.")
    
    with open(ETL_SQL, 'r') as f:
        sql_content = f.read()
    st.code(sql_content, language="sql")

# TAB 3: PREDICTIVE FORECASTING
with tab3:
    st.subheader("🤖 Machine Learning Revenue Forecasting & Churn Alert System")
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("ML Model R² Score", f"{metrics['r2_score']}")
    m_col2.metric("ML Forecast RMSE", f"${metrics['ml_model_rmse']:,.2f}")
    m_col3.metric("MAPE % Error", f"{metrics['mape_pct']}%")
    m_col4.metric("Accuracy Improvement", f"+{metrics['accuracy_improvement_pct']}%", delta="vs Naive Baseline")

    st.markdown("---")
    st.subheader("Next Month Predicted Revenue per Client")
    st.dataframe(
        forecast_df[['client_id', 'client_name', 'gross_revenue', 'predicted_next_month_rev', 'forecast_diff', 'churn_risk_flag']]
        .rename(columns={
            'gross_revenue': 'Current Month Rev ($)',
            'predicted_next_month_rev': 'Forecasted Next Month Rev ($)',
            'forecast_diff': 'Expected Delta ($)',
            'churn_risk_flag': 'Churn Risk Flag'
        }),
        use_container_width=True
    )

# TAB 4: AUTOMATED REPORTS
with tab4:
    st.subheader("📄 Automated Client Financial Reporting Models")
    st.markdown("Automated generation of styled Excel financial models via `openpyxl` and Google Sheets API payload via `gspread`.")

    rep_col1, rep_col2 = st.columns(2)

    with rep_col1:
        st.markdown("### 📊 Excel Reporting Model (`openpyxl`)")
        st.write("Generates formatted Excel workbooks with custom navy styling, KPI metric cards, auto-fit columns, and embedded openpyxl charts.")
        
        if os.path.exists(OUTPUT_EXCEL):
            with open(OUTPUT_EXCEL, "rb") as f:
                st.download_button(
                    label="📥 Download ClientPulse Financial Report (.xlsx)",
                    data=f,
                    file_name="ClientPulse_Financial_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    with rep_col2:
        st.markdown("### 🌐 Google Sheets API Automation (`gspread`)")
        st.write("Automatically pushes payload to Google Sheets API endpoint or exports synchronized CSV payload.")
        st.code("""
# GSheets API Sync Code Snippet
import gspread
client = gspread.service_account(filename="service_account.json")
sh = client.open("ClientPulse Executive Summary")
sh.sheet1.update(data_payload)
        """, language="python")

st.markdown("---")
st.caption("ClientPulse Analytics Pipeline | Developed for Fischer Jordan Analyst Assessment")
