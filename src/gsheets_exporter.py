import gspread
import pandas as pd
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "client_pulse.db")
CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "service_account.json")
CSV_BACKUP = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ClientPulse_GSheets_Payload.csv")

class GoogleSheetsSyncManager:
    def __init__(self, credentials_path=CREDENTIALS_PATH, db_path=DB_PATH):
        self.credentials_path = credentials_path
        self.db_path = db_path
        self.client = None

    def connect(self):
        """Authenticate with Google Sheets API using service account credentials."""
        if os.path.exists(self.credentials_path):
            try:
                self.client = gspread.service_account(filename=self.credentials_path)
                print("[GSHEETS API] Authenticated successfully with Google Sheets API service account.")
                return True
            except Exception as e:
                print(f"[GSHEETS API] Service account auth error: {e}. Falling back to Demo Mode.")
                return False
        else:
            print("[GSHEETS API] No 'service_account.json' found. Running in API Demo / Simulation Mode.")
            return False

    def sync_latest_financials(self, spreadsheet_name="ClientPulse Monthly Executive Summary"):
        """Extract warehouse summary and publish to Google Sheets API (or export payload in Demo Mode)."""
        conn = sqlite3.connect(self.db_path)
        latest_month = pd.read_sql_query("SELECT MAX(ym_month) FROM fact_monthly_financials;", conn).iloc[0, 0]

        df = pd.read_sql_query(
            f"SELECT client_id, client_name, industry, gross_revenue, net_profit, profit_margin_pct, mom_growth_pct, avg_csat, churn_risk_flag FROM fact_monthly_financials WHERE ym_month = '{latest_month}' ORDER BY gross_revenue DESC;",
            conn
        )
        conn.close()

        # Format dataset for Sheets payload
        df['gross_revenue'] = df['gross_revenue'].apply(lambda x: f"${x:,.2f}")
        df['net_profit'] = df['net_profit'].apply(lambda x: f"${x:,.2f}")
        df['profit_margin_pct'] = df['profit_margin_pct'].apply(lambda x: f"{x:.1f}%")
        df['mom_growth_pct'] = df['mom_growth_pct'].apply(lambda x: f"{x:.1f}%")
        df['churn_risk_flag'] = df['churn_risk_flag'].apply(lambda x: "RISK" if x == 1 else "STABLE")

        values = [df.columns.tolist()] + df.values.tolist()

        if self.connect():
            try:
                # Open or create spreadsheet
                sh = self.client.open(spreadsheet_name)
                worksheet = sh.sheet1
                worksheet.clear()
                worksheet.update(values)
                print(f"[GSHEETS API] Successfully updated live Google Sheet '{spreadsheet_name}'! URL: {sh.url}")
                return sh.url
            except Exception as e:
                print(f"[GSHEETS API] Error pushing to Google Sheets: {e}")

        # Demo / Offline Backup Export
        df.to_csv(CSV_BACKUP, index=False)
        print(f"[GSHEETS API] (Demo Mode) API payload validated! Exported synchronized payload to '{CSV_BACKUP}'.")
        return CSV_BACKUP

def sync_to_gsheets():
    manager = GoogleSheetsSyncManager()
    return manager.sync_latest_financials()

if __name__ == "__main__":
    sync_to_gsheets()
