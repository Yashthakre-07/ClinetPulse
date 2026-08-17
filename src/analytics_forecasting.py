import pandas as pd
import numpy as np
import sqlite3
import os
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error, r2_score, mean_absolute_percentage_error

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "client_pulse.db")

class BusinessAnalyticsPredictor:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.df = None
        self.model = None
        self.metrics = {}

    def load_data(self):
        conn = sqlite3.connect(self.db_path)
        self.df = pd.read_sql_query("SELECT * FROM fact_monthly_features ORDER BY client_id, ym_month;", conn)
        conn.close()
        return self.df

    def compute_business_kpis(self):
        """Calculate executive quantitative metrics."""
        if self.df is None:
            self.load_data()

        latest_month = self.df['ym_month'].max()
        latest_df = self.df[self.df['ym_month'] == latest_month]

        total_monthly_rev = latest_df['gross_revenue'].sum()
        total_arr = total_monthly_rev * 12
        avg_arpu = latest_df['gross_revenue'].mean()
        avg_margin = latest_df['profit_margin_pct'].mean()
        churn_risk_count = latest_df['churn_risk_flag'].sum()
        active_clients = len(latest_df)

        return {
            "latest_month": latest_month,
            "total_monthly_revenue": round(total_monthly_rev, 2),
            "annual_run_rate_arr": round(total_arr, 2),
            "arpu": round(avg_arpu, 2),
            "avg_profit_margin_pct": round(avg_margin, 2),
            "churn_risk_clients": int(churn_risk_count),
            "active_clients": active_clients
        }

    def train_predictive_forecast_model(self):
        """Build predictive model to forecast next month revenue and evaluate accuracy improvement."""
        if self.df is None:
            self.load_data()

        df = self.df.copy()

        # Create target variable: Next Month's Revenue
        df['target_next_month_rev'] = df.groupby('client_id')['gross_revenue'].shift(-1)
        
        # Drop rows where target is missing (last month for each client)
        dataset = df.dropna(subset=['target_next_month_rev']).copy()

        feature_cols = [
            'gross_revenue', 'lag_1_revenue', 'lag_2_revenue', 
            'rolling_3m_avg_revenue', 'rolling_3m_std', 
            'tenure_months', 'avg_csat', 'cost_to_revenue_ratio',
            'ticket_per_10k_rev', 'contract_tier_code'
        ]

        X = dataset[feature_cols]
        y = dataset['target_next_month_rev']

        # Train/Test Split (Time-based split: last 20% records for testing)
        split_idx = int(len(dataset) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        # Naive Baseline Model (Using current month revenue as next month's forecast)
        y_naive_pred = X_test['gross_revenue']
        naive_rmse = root_mean_squared_error(y_test, y_naive_pred)

        # ML Predictive Model (Ridge Regression / Random Forest)
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)

        y_ml_pred = self.model.predict(X_test)
        ml_rmse = root_mean_squared_error(y_test, y_ml_pred)
        ml_r2 = r2_score(y_test, y_ml_pred)
        ml_mape = mean_absolute_percentage_error(y_test, y_ml_pred)

        # Accuracy Improvement Calculation %
        accuracy_improvement_pct = round(((naive_rmse - ml_rmse) / naive_rmse) * 100.0, 2)

        self.metrics = {
            "naive_baseline_rmse": round(naive_rmse, 2),
            "ml_model_rmse": round(ml_rmse, 2),
            "r2_score": round(ml_r2, 4),
            "mape_pct": round(ml_mape * 100, 2),
            "accuracy_improvement_pct": accuracy_improvement_pct
        }

        # Predict Next Month's Revenue for Current Active Clients
        latest_month = self.df['ym_month'].max()
        latest_active = self.df[self.df['ym_month'] == latest_month].copy()
        
        X_latest = latest_active[feature_cols]
        latest_active['predicted_next_month_rev'] = self.model.predict(X_latest)
        latest_active['forecast_diff'] = latest_active['predicted_next_month_rev'] - latest_active['gross_revenue']

        print(f"[MODEL TRAINED] R2 Score: {ml_r2:.3f} | RMSE: ${ml_rmse:.2f} | Forecast Accuracy Improved by {accuracy_improvement_pct}% vs Naive Baseline!")
        return latest_active, self.metrics

    def generate_actionable_insights(self):
        """Surface strategic business insights for client strategy."""
        if self.df is None:
            self.load_data()

        latest_month = self.df['ym_month'].max()
        latest_df = self.df[self.df['ym_month'] == latest_month]

        # Top Growth Accounts
        top_growth = latest_df.sort_values(by='mom_growth_pct', ascending=False).head(3)[
            ['client_id', 'client_name', 'gross_revenue', 'mom_growth_pct', 'industry']
        ]

        # Churn At-Risk Clients
        churn_risk = latest_df[latest_df['churn_risk_flag'] == 1][
            ['client_id', 'client_name', 'gross_revenue', 'avg_csat', 'sla_breaches', 'mom_growth_pct']
        ]

        return {
            "top_growth_clients": top_growth,
            "churn_risk_clients": churn_risk
        }

def run_analytics():
    predictor = BusinessAnalyticsPredictor()
    kpis = predictor.compute_business_kpis()
    forecast_df, metrics = predictor.train_predictive_forecast_model()
    insights = predictor.generate_actionable_insights()
    return kpis, forecast_df, metrics, insights

if __name__ == "__main__":
    run_analytics()
