import os
import mlflow
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import attribution_models
import funnel_analytics

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
    
    # Establish the professional MLflow Experiment Container
    mlflow.set_experiment("Multi_Channel_Marketing_Hub")
    
    with mlflow.start_run(run_name="Full_Marketing_Audit_Execution"):
        print("🚀 Step 1: Processing Multi-Touch Attribution...")
        spend_df, click_df = attribution_models.get_analytics_data()
        
        if click_df.empty or spend_df.empty:
            print("Database tables are empty. Ingest data via S3 first.")
            return
            
        click_df["timestamp"] = pd.to_datetime(click_df["timestamp"])
        click_df = click_df.sort_values(by=["user_id", "timestamp"])
        conversions = click_df[click_df["page_type"] == "payment_confirmation"].copy()
        
        first_touch_results = []
        last_touch_results = []
        time_decay_results = []
        
        for _, conversion in conversions.iterrows():
            user = conversion["user_id"]
            conv_time = conversion["timestamp"]
            rev = float(conversion["revenue"])
            
            journey = click_df[
                (click_df["user_id"] == user) & 
                (click_df["timestamp"] <= conv_time) & 
                (click_df["traffic_source"] != "Direct")
            ]
            if journey.empty:
                continue
                
            first_touch_results.append({"channel": journey.iloc[0]["traffic_source"], "revenue": rev})
            last_touch_results.append({"channel": journey.iloc[-1]["traffic_source"], "revenue": rev})
            
            journey = journey.copy()
            journey["hours_to_conv"] = (conv_time - journey["timestamp"]).dt.total_seconds() / 3600.0
            journey["weight"] = 2 ** (-journey["hours_to_conv"] / 72.0)
            
            total_weight = journey["weight"].sum()
            if total_weight > 0:
                journey["allocated_revenue"] = (journey["weight"] / total_weight) * rev
                for _, row in journey.iterrows():
                    time_decay_results.append({"channel": row["traffic_source"], "revenue": row["allocated_revenue"]})

        ft_df = pd.DataFrame(first_touch_results).groupby("channel")["revenue"].sum().reset_index()
        lt_df = pd.DataFrame(last_touch_results).groupby("channel")["revenue"].sum().reset_index()
        td_df = pd.DataFrame(time_decay_results).groupby("channel")["revenue"].sum().reset_index()
        
        summary_spend = spend_df.groupby("channel")[["ad_spend", "clicks"]].sum().reset_index()
        attr_metrics = summary_spend.merge(ft_df, on="channel", how="left").rename(columns={"revenue": "first_touch_rev"})
        attr_metrics = attr_metrics.merge(lt_df, on="channel", how="left").rename(columns={"revenue": "last_touch_rev"})
        attr_metrics = attr_metrics.merge(td_df, on="channel", how="left").rename(columns={"revenue": "time_decay_rev"}).fillna(0.0)
        
        # 💾 Write Analysis 1 back to MySQL Table
        attr_metrics.to_sql("summary_attribution_metrics", con=engine, if_exists="replace", index=False)
        print("✅ Saved Attribution Summary to MySQL.")
        
        # 📈 Log Analysis 1 to MLflow
        for _, row in attr_metrics.iterrows():
            ch = row["channel"].replace(" ", "_").lower()
            mlflow.log_metric(f"attr_{ch}_ad_spend", float(row["ad_spend"]))
            mlflow.log_metric(f"attr_{ch}_time_decay_rev", float(row["time_decay_rev"]))

        print("\n⏳ Step 2: Processing Funnel Velocity Analysis...")
        landing = click_df[click_df["page_type"] == "landing_page"].groupby("session_id")["timestamp"].min().reset_index().rename(columns={"timestamp": "landing_time"})
        cart = click_df[click_df["page_type"] == "cart"].groupby("session_id")["timestamp"].min().reset_index().rename(columns={"timestamp": "cart_time"})
        payment = click_df[click_df["page_type"] == "payment_confirmation"].groupby("session_id")["timestamp"].min().reset_index().rename(columns={"timestamp": "payment_time"})
        
        funnel = landing.merge(cart, on="session_id", how="left").merge(payment, on="session_id", how="left")
        total_landing = len(funnel)
        total_cart = len(funnel[funnel["cart_time"].notna()])
        total_payment = len(funnel[funnel["cart_time"].notna() & funnel["payment_time"].notna()])
        
        c_conv = (total_cart / total_landing) * 100 if total_landing > 0 else 0
        p_conv = (total_payment / total_cart) * 100 if total_cart > 0 else 0
        overall_conv = (total_payment / total_landing) * 100 if total_landing > 0 else 0
        
        funnel["landing_to_cart_mins"] = (funnel["cart_time"] - funnel["landing_time"]).dt.total_seconds() / 60.0
        funnel["cart_to_payment_mins"] = (funnel["payment_time"] - funnel["cart_time"]).dt.total_seconds() / 60.0
        avg_time_to_cart = funnel["landing_to_cart_mins"].mean()
        avg_time_to_payment = funnel["cart_to_payment_mins"].mean()

        funnel_data = pd.DataFrame([
            {"stage_name": "Stage 1: Landing Page", "session_count": total_landing, "conversion_rate": 100.0, "dropoff_rate": 0.0},
            {"stage_name": "Stage 2: Cart Additions", "session_count": total_cart, "conversion_rate": round(c_conv, 2), "dropoff_rate": round(100 - c_conv, 2)},
            {"stage_name": "Stage 3: Payment Confirmation", "session_count": total_payment, "conversion_rate": round(p_conv, 2), "dropoff_rate": round(100 - p_conv, 2)}
        ])
        
        # 💾 Write Analysis 2 back to MySQL Table
        funnel_data.to_sql("summary_funnel_metrics", con=engine, if_exists="replace", index=False)
        print("✅ Saved Funnel Summary to MySQL.")
        
        # 📈 Log Analysis 2 to MLflow
        mlflow.log_metric("funnel_landing_sessions", int(total_landing))
        mlflow.log_metric("funnel_cart_conversion_pct", float(c_conv))
        mlflow.log_metric("funnel_checkout_conversion_pct", float(p_conv))
        mlflow.log_metric("funnel_overall_conversion_pct", float(overall_conv))
        mlflow.log_metric("velocity_avg_minutes_to_cart", float(pd.Series(avg_time_to_cart).fillna(0.0).iloc[0]))
        mlflow.log_metric("velocity_avg_minutes_to_payment", float(pd.Series(avg_time_to_payment).fillna(0.0).iloc[0]))

        print("\n💼 Step 3: Processing Advanced Efficiency Analysis (CPC / CPA)...")
        efficiency_results = []
        for _, row in attr_metrics.iterrows():
            ch = row["channel"]
            spend = float(row["ad_spend"])
            clicks = int(row["clicks"])
            td_rev = float(row["time_decay_rev"])
            
            cpc = spend / clicks if clicks > 0 else 0.0
            # Continuous contribution weighting calculation
            cpa = spend / (td_rev / 50.0) if td_rev > 0 else 0.0 
            
            efficiency_results.append({
                "channel": ch,
                "cpc": round(cpc, 2),
                "cpa": round(cpa, 2)
            })
            
            # 📈 Log Analysis 3 to MLflow
            ch_slug = ch.replace(" ", "_").lower()
            mlflow.log_metric(f"efficiency_{ch_slug}_cpc", round(cpc, 2))
            mlflow.log_metric(f"efficiency_{ch_slug}_cpa", round(cpa, 2))
            
        eff_df = pd.DataFrame(efficiency_results)
        # 💾 Write Analysis 3 back to MySQL Table
        eff_df.to_sql("summary_efficiency_metrics", con=engine, if_exists="replace", index=False)
        print("✅ Saved Efficiency (CPC/CPA) Summary to MySQL.")
        
        print("\n🎉 Telemetry for all 3 analyses has been successfully recorded in MLflow!")

if __name__ == "__main__":
    run_complete_analysis_pipeline()
