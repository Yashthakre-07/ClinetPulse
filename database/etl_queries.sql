-- ClientPulse: Complex ETL Transformations & Warehouse Consolidation Query
-- Demonstrating CTEs, Window Functions (LAG, SUM OVER, AVG OVER), Joins, and Aggregations

-- Drop target warehouse table if exists
DROP TABLE IF EXISTS fact_monthly_financials;

-- Create Validated Warehouse Fact Table
CREATE TABLE fact_monthly_financials AS
WITH monthly_raw_aggregation AS (
    -- CTE 1: Consolidate transactional revenue and expenses by Client and Month
    SELECT 
        client_id,
        strftime('%Y-%m', transaction_date) AS ym_month,
        SUM(monthly_fee) AS gross_revenue,
        SUM(operational_cost) AS total_cost,
        SUM(monthly_fee) - SUM(operational_cost) AS net_profit
    FROM raw_transactions
    WHERE payment_status = 'Paid'
    GROUP BY client_id, strftime('%Y-%m', transaction_date)
),
monthly_support_aggregation AS (
    -- CTE 2: Aggregate monthly support tickets and average CSAT per client
    SELECT 
        client_id,
        strftime('%Y-%m', log_date) AS ym_month,
        SUM(tickets_opened) AS total_tickets,
        ROUND(AVG(csat_score), 2) AS avg_csat,
        SUM(CASE WHEN sla_met_flag = 0 THEN 1 ELSE 0 END) AS sla_breaches
    FROM raw_support_logs
    GROUP BY client_id, strftime('%Y-%m', log_date)
),
consolidated_warehouse AS (
    -- CTE 3: Multi-Relational Join & Advanced Window Functions
    SELECT 
        c.client_id,
        c.client_name,
        c.industry,
        c.region,
        c.contract_tier,
        m.ym_month,
        m.gross_revenue,
        m.total_cost,
        m.net_profit,
        
        -- Window Function 1: Prior Month Revenue via LAG()
        LAG(m.gross_revenue, 1, 0.0) OVER (
            PARTITION BY c.client_id 
            ORDER BY m.ym_month
        ) AS prior_month_revenue,

        -- Window Function 2: 3-Month Moving Average Revenue
        AVG(m.gross_revenue) OVER (
            PARTITION BY c.client_id 
            ORDER BY m.ym_month 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS rolling_3m_avg_revenue,

        -- Window Function 3: Cumulative Lifetime Revenue per Client
        SUM(m.gross_revenue) OVER (
            PARTITION BY c.client_id 
            ORDER BY m.ym_month
        ) AS cumulative_lifetime_revenue,

        COALESCE(s.total_tickets, 0) AS total_tickets,
        COALESCE(s.avg_csat, 5.0) AS avg_csat,
        COALESCE(s.sla_breaches, 0) AS sla_breaches

    FROM monthly_raw_aggregation m
    INNER JOIN raw_clients c ON m.client_id = c.client_id
    LEFT JOIN monthly_support_aggregation s 
        ON m.client_id = s.client_id 
        AND m.ym_month = s.ym_month
)
SELECT 
    client_id,
    client_name,
    industry,
    region,
    contract_tier,
    ym_month,
    gross_revenue,
    total_cost,
    net_profit,
    prior_month_revenue,
    
    -- Calculated Feature 1: Month-over-Month (MoM) Growth Percentage
    CASE 
        WHEN prior_month_revenue = 0 THEN 0.0
        ELSE ROUND(((gross_revenue - prior_month_revenue) / prior_month_revenue) * 100.0, 2)
    END AS mom_growth_pct,

    ROUND(rolling_3m_avg_revenue, 2) AS rolling_3m_avg_revenue,
    ROUND(cumulative_lifetime_revenue, 2) AS cumulative_lifetime_revenue,
    ROUND((net_profit / gross_revenue) * 100.0, 2) AS profit_margin_pct,
    total_tickets,
    avg_csat,
    sla_breaches,
    
    -- Calculated Feature 2: Client Risk Indicator
    CASE 
        WHEN avg_csat < 3.0 OR sla_breaches >= 2 OR gross_revenue < prior_month_revenue * 0.85 THEN 1
        ELSE 0
    END AS churn_risk_flag

FROM consolidated_warehouse;
