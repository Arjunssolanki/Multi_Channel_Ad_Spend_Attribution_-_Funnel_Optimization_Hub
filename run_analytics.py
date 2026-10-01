import os
import mlflow
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

import attribution_models
from analytics_modules.marketing_attribution import calculate_attribution_and_efficiency
from analytics_modules.funnel_velocity import calculate_funnel_and_velocity
from analytics_modules.dashboard_pages import calculate_bi_dashboard_pages

load_dotenv()

def get_db_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", 3306)
    database = os.getenv("DB_NAME")
    return create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")

def run_complete_analysis_pipeline():
    engine = get_db_engine()
    mlflow.set_experiment("Multi_Channel_Marketing_Hub")
    
    with mlflow.start_run(run_name="Full_Marketing_Audit_Execution"):
        print("🚀 Step 1: Loading raw data fields from MySQL Lakehouse...")
        spend_df, click_df = attribution_models.get_analytics_data()
        
        if click_df.empty or spend_df.empty:
            print("Database tables are empty. Ingest data via S3 first.")
            return

        print("🔮 Step 2: Computing Multi-Touch Attribution & Efficiency Modules...")
        attr_metrics, eff_df = calculate_attribution_and_efficiency(spend_df, click_df)
        attr_metrics.to_sql("summary_attribution_metrics", con=engine, if_exists="replace", index=False)
        eff_df.to_sql("summary_efficiency_metrics", con=engine, if_exists="replace", index=False)
        print("✅ Saved Page 1 Core Metrics to MySQL.")
        
        for _, row in attr_metrics.iterrows():
            ch = row["channel"].replace(" ", "_").lower()
            mlflow.log_metric(f"attr_{ch}_ad_spend", float(row["ad_spend"]))
            mlflow.log_metric(f"attr_{ch}_time_decay_rev", float(row["time_decay_rev"]))
        for _, row in eff_df.iterrows():
            ch_slug = row["channel"].replace(" ", "_").lower()
            mlflow.log_metric(f"efficiency_{ch_slug}_cpc", float(row["cpc"]))
            mlflow.log_metric(f"efficiency_{ch_slug}_cpa", float(row["cpa"]))

        print("⏳ Step 3: Computing Funnel Step Velocity Real-Time Analytics...")
        funnel_data, total_l, c_conv, p_conv, overall_conv, v_cart, v_pay, landing, cart, payment = calculate_funnel_and_velocity(click_df)
        funnel_data.to_sql("summary_funnel_metrics", con=engine, if_exists="replace", index=False)
        print("✅ Saved Funnel Summary to MySQL with dynamic velocity fields.")
        
        mlflow.log_metric("funnel_landing_sessions", int(total_l))
        mlflow.log_metric("funnel_cart_conversion_pct", float(c_conv))
        mlflow.log_metric("funnel_checkout_conversion_pct", float(p_conv))
        mlflow.log_metric("funnel_overall_conversion_pct", float(overall_conv))
        mlflow.log_metric("velocity_avg_minutes_to_cart", v_cart)
        mlflow.log_metric("velocity_avg_minutes_to_payment", v_pay)

        print("📈 Step 4: Computing Page 2 & Page 3 Business Intelligence Layers...")
        cohort_df, realloc_df = calculate_bi_dashboard_pages(click_df, attr_metrics, landing, cart, payment)
        cohort_df.to_sql("bi_page2_cohort_matrix", con=engine, if_exists="replace", index=False)
        realloc_df.to_sql("bi_page3_budget_optimization", con=engine, if_exists="replace", index=False)
        print("✅ Saved Page 2 Cohort Matrix and Page 3 Optimization Tables to MySQL.")
        
        print("\n🎉 Telemetry pipelines successfully executed! Open Power BI and click Refresh.")

if __name__ == "__main__":
    run_complete_analysis_pipeline()
