import os
import sys
import time

from src.database_setup import init_db
from src.etl_pipeline import run_etl
from src.analytics_forecasting import run_analytics
from src.excel_exporter import generate_styled_excel_report
from src.gsheets_exporter import sync_to_gsheets

def print_banner():
    print("=" * 70)
    print("  CLIENTPULSE — SQL & PYTHON BUSINESS ANALYTICS ETL PIPELINE  ")
    print("=" * 70)

def main():
    start_time = time.time()
    print_banner()

    # Step 1: Database & SQL Warehouse
    print("\n--- STEP 1: INITIALIZING RELATIONAL DATABASE & SQL WAREHOUSE ---")
    init_db()

    # Step 2: Python ETL Pipeline & Feature Engineering
    print("\n--- STEP 2: RUNNING PYTHON ETL & FEATURE ENGINEERING PIPELINE ---")
    df_features = run_etl()

    # Step 3: Predictive Analytics & Revenue Forecasting Model
    print("\n--- STEP 3: QUANTITATIVE ANALYTICS & PREDICTIVE FORECASTING ---")
    kpis, forecast_df, metrics, insights = run_analytics()

    # Step 4: Automated Excel Reporting Model (openpyxl)
    print("\n--- STEP 4: GENERATING AUTOMATED CLIENT EXCEL MODEL (openpyxl) ---")
    excel_file = generate_styled_excel_report()

    # Step 5: Google Sheets API Integration (gspread)
    print("\n--- STEP 5: GOOGLE SHEETS API AUTOMATION (gspread) ---")
    sheets_output = sync_to_gsheets()

    elapsed = round(time.time() - start_time, 2)

    # Print Executive Summary Table
    print("\n" + "=" * 70)
    print("                      PIPELINE EXECUTION SUMMARY                    ")
    print("=" * 70)
    print(f" Total Monthly Portfolio Revenue : ${kpis['total_monthly_revenue']:,.2f}")
    print(f" Annualized Run Rate (ARR)      : ${kpis['annual_run_rate_arr']:,.2f}")
    print(f" Average Account Revenue (ARPU)  : ${kpis['arpu']:,.2f}")
    print(f" Average Gross Margin           : {kpis['avg_profit_margin_pct']}%")
    print(f" Active Clients Monitored       : {kpis['active_clients']}")
    print(f" Churn Risk Alerts Detected     : {kpis['churn_risk_clients']}")
    print("-" * 70)
    print(f" ML Model Forecast RMSE         : ${metrics['ml_model_rmse']:,.2f}")
    print(f" Forecast Accuracy Improvement  : +{metrics['accuracy_improvement_pct']}% vs Naive Baseline")
    print(f" Generated Excel Report         : {excel_file}")
    print(f" Google Sheets API Destination  : {sheets_output}")
    print(f" Pipeline Execution Speed       : {elapsed} seconds")
    print("=" * 70)
    print("[SUCCESS] All pipeline stages executed successfully!\n")

if __name__ == "__main__":
    main()
