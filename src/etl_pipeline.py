import pandas as pd
import numpy as np
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "client_pulse.db")

class ClientPulseETL:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.raw_data = None
        self.cleaned_data = None
        self.feature_data = None

    def extract(self):
        """Extract data from SQL warehouse tables."""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM fact_monthly_financials ORDER BY client_id, ym_month;"
        self.raw_data = pd.read_sql_query(query, conn)
        conn.close()
        print(f"[EXTRACT] Successfully extracted {len(self.raw_data)} records from SQL Warehouse.")
        return self.raw_data

    def validate_and_clean(self):
        """Perform schema validation, type enforcement, missing value handling, and outlier checks."""
        if self.raw_data is None:
            self.extract()

        df = self.raw_data.copy()

        # 1. Null handling & default imputation
        df['prior_month_revenue'] = df['prior_month_revenue'].fillna(0.0)
        df['mom_growth_pct'] = df['mom_growth_pct'].fillna(0.0)
        df['avg_csat'] = df['avg_csat'].fillna(4.5) # Default neutral-high CSAT
        df['total_tickets'] = df['total_tickets'].fillna(0).astype(int)

        # 2. Schema type assertion
        df['gross_revenue'] = pd.to_numeric(df['gross_revenue'], errors='coerce')
        df['total_cost'] = pd.to_numeric(df['total_cost'], errors='coerce')
        df['net_profit'] = pd.to_numeric(df['net_profit'], errors='coerce')

        # 3. Validation Check: Ensure no negative revenues or invalid formats
        invalid_rows = df[df['gross_revenue'] < 0]
        if len(invalid_rows) > 0:
            print(f"[WARN] Found {len(invalid_rows)} invalid negative revenue records. Removing...")
            df = df[df['gross_revenue'] >= 0]

        self.cleaned_data = df
        print(f"[CLEAN] Validation & cleaning complete. Clean dataset size: {len(self.cleaned_data)} rows.")
        return self.cleaned_data

    def engineer_features(self):
        """Engineer predictive ML features (Lagged variables, rolling statistics, ratio indicators)."""
        if self.cleaned_data is None:
            self.validate_and_clean()

        df = self.cleaned_data.copy()
        df = df.sort_values(by=['client_id', 'ym_month']).reset_index(drop=True)

        # 1. Lagged Features (1-month & 2-month prior revenue)
        df['lag_1_revenue'] = df.groupby('client_id')['gross_revenue'].shift(1).fillna(df['gross_revenue'])
        df['lag_2_revenue'] = df.groupby('client_id')['gross_revenue'].shift(2).fillna(df['lag_1_revenue'])

        # 2. Rolling Statistics (3-month Volatility / Standard Deviation)
        df['rolling_3m_std'] = df.groupby('client_id')['gross_revenue'].transform(
            lambda x: x.rolling(3, min_periods=1).std()
        ).fillna(0.0)

        # 3. Client Tenure Count (Number of months active)
        df['tenure_months'] = df.groupby('client_id').cumcount() + 1

        # 4. Expense Ratio & Ticket Intensity
        df['cost_to_revenue_ratio'] = np.where(
            df['gross_revenue'] > 0, 
            df['total_cost'] / df['gross_revenue'], 
            0.0
        )
        df['ticket_per_10k_rev'] = np.where(
            df['gross_revenue'] > 0, 
            (df['total_tickets'] / df['gross_revenue']) * 10000.0, 
            0.0
        )

        # 5. Encoding Contract Tier
        contract_map = {'Enterprise': 3, 'Mid-Market': 2, 'SMB': 1}
        df['contract_tier_code'] = df['contract_tier'].map(contract_map).fillna(1)

        self.feature_data = df
        print(f"[FEATURE ENGINE] Engineered 7 predictive features successfully.")
        return self.feature_data

    def save_engineered_features(self):
        """Save feature-engineered table back to SQLite database warehouse."""
        if self.feature_data is None:
            self.engineer_features()

        conn = sqlite3.connect(self.db_path)
        self.feature_data.to_sql('fact_monthly_features', conn, if_exists='replace', index=False)
        conn.close()
        print("[LOAD] Saved engineered features table 'fact_monthly_features' to SQLite warehouse.")

def run_etl():
    etl = ClientPulseETL()
    etl.extract()
    etl.validate_and_clean()
    etl.engineer_features()
    etl.save_engineered_features()
    return etl.feature_data

if __name__ == "__main__":
    run_etl()
