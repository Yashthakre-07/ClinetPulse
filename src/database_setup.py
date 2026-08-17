import sqlite3
import os
import random
import pandas as pd
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "client_pulse.db")
SCHEMA_SQL = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "schema.sql")
ETL_SQL = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "etl_queries.sql")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initializes schema and seeds realistic transactional data."""
    conn = get_connection()
    cursor = conn.cursor()

    # Read and execute schema
    with open(SCHEMA_SQL, 'r') as f:
        cursor.executescript(f.read())
    conn.commit()

    # Seed Raw Clients
    clients_data = [
        ("CLT-101", "Apex Health Systems", "Healthcare", "North America", "2024-01-15", "Enterprise"),
        ("CLT-102", "Finova Capital", "FinTech", "North America", "2024-02-01", "Enterprise"),
        ("CLT-103", "Nexus Logistics", "Logistics", "Europe", "2024-01-20", "Mid-Market"),
        ("CLT-104", "Quantum Retail", "E-Commerce", "APAC", "2024-03-10", "Mid-Market"),
        ("CLT-105", "Vanguard BioMed", "Healthcare", "North America", "2024-02-15", "Enterprise"),
        ("CLT-106", "Starlight Media", "Media", "Europe", "2024-04-01", "SMB"),
        ("CLT-107", "BlueSky Tech", "SaaS", "North America", "2024-01-05", "Enterprise"),
        ("CLT-108", "Global Trade Corp", "Logistics", "APAC", "2024-03-01", "Mid-Market"),
        ("CLT-109", "CyberShield Security", "SaaS", "North America", "2024-04-15", "Enterprise"),
        ("CLT-110", "OmniPay Solutions", "FinTech", "Europe", "2024-02-28", "Mid-Market"),
        ("CLT-111", "GreenGrid Energy", "CleanTech", "North America", "2024-05-01", "SMB"),
        ("CLT-112", "Velocity Mobility", "Automotive", "APAC", "2024-01-12", "Mid-Market")
    ]

    cursor.executemany("""
        INSERT INTO raw_clients (client_id, client_name, industry, region, onboard_date, contract_tier)
        VALUES (?, ?, ?, ?, ?, ?)
    """, clients_data)

    # Seed 18 Months of Transactional Data per Client
    random.seed(42) # Deterministic for reproducible interviews
    start_date = datetime(2025, 1, 1)

    transactions = []
    support_logs = []

    for client in clients_data:
        client_id = client[0]
        contract_tier = client[5]
        
        base_fee = 25000 if contract_tier == "Enterprise" else (12000 if contract_tier == "Mid-Market" else 5000)
        base_cost = base_fee * random.uniform(0.35, 0.50)

        current_fee = base_fee
        for m in range(18):
            dt = start_date + timedelta(days=m * 30)
            date_str = dt.strftime("%Y-%m-%d")
            
            # Trend revenue with small random fluctuations + occasional churn signal
            growth_factor = random.uniform(0.96, 1.06)
            if client_id == "CLT-106" and m >= 12: # Simulated declining client
                growth_factor = 0.85
            
            current_fee = round(current_fee * growth_factor, 2)
            cost = round(current_fee * random.uniform(0.35, 0.45), 2)
            status = 'Paid' if random.random() > 0.03 else 'Pending'

            transactions.append((client_id, date_str, current_fee, cost, status))

            # Support log
            tickets = random.randint(0, 5) if client_id != "CLT-106" else random.randint(4, 9)
            csat = round(random.uniform(4.0, 5.0), 2) if tickets <= 3 else round(random.uniform(2.1, 3.8), 2)
            sla_met = 1 if csat >= 3.5 else 0

            support_logs.append((client_id, date_str, tickets, sla_met, csat))

    cursor.executemany("""
        INSERT INTO raw_transactions (client_id, transaction_date, monthly_fee, operational_cost, payment_status)
        VALUES (?, ?, ?, ?, ?)
    """, transactions)

    cursor.executemany("""
        INSERT INTO raw_support_logs (client_id, log_date, tickets_opened, sla_met_flag, csat_score)
        VALUES (?, ?, ?, ?, ?)
    """, support_logs)

    conn.commit()
    
    # Run ETL query script to generate warehouse tables
    with open(ETL_SQL, 'r') as f:
        cursor.executescript(f.read())
    conn.commit()

    conn.close()
    print("[OK] Database initialized, seeded, and SQL ETL warehouse created successfully!")

if __name__ == "__main__":
    init_db()
