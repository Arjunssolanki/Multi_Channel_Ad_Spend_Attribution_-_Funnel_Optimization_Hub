import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_analytics_data():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", 3306)
    database = os.getenv("DB_NAME")
    
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")
    
    spend_query = "SELECT channel, spend_date, ad_spend, clicks FROM marketing_spend_logs;"
    click_query = "SELECT user_id, session_id, timestamp, traffic_source, page_type, revenue FROM web_clickstream_logs;"
    
    spend_df = pd.read_sql(spend_query, engine)
    click_df = pd.read_sql(click_query, engine)
    
    return spend_df, click_df

def compute_attribution():
    spend_df, click_df = get_analytics_data()
    
    if click_df.empty or spend_df.empty:
        print("Awaiting raw transactional records in database tables.")
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
            
        first_channel = journey.iloc[0]["traffic_source"]
        first_touch_results.append({"channel": first_channel, "revenue": rev})
        
        last_channel = journey.iloc[-1]["traffic_source"]
        last_touch_results.append({"channel": last_channel, "revenue": rev})
        
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
    
    metrics = summary_spend.merge(ft_df, on="channel", how="left").rename(columns={"revenue": "first_touch_rev"})
    metrics = metrics.merge(lt_df, on="channel", how="left").rename(columns={"revenue": "last_touch_rev"})
    metrics = metrics.merge(td_df, on="channel", how="left").rename(columns={"revenue": "time_decay_rev"})
    
    metrics = metrics.fillna(0.0)
    
    print("\n================== EXECUTIVE MARKETING ATTRIBUTION METRICS ==================")
    print(metrics.to_string(index=False))
    print("=============================================================================\n")

if __name__ == "__main__":
    compute_attribution()
