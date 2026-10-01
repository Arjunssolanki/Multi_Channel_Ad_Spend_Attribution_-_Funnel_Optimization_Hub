import pandas as pd

def calculate_attribution_and_efficiency(spend_df, click_df):
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
    
    efficiency_results = []
    for _, row in attr_metrics.iterrows():
        ch = row["channel"]
        spend = float(row["ad_spend"])
        clicks = int(row["clicks"])
        td_rev = float(row["time_decay_rev"])
        
        cpc = spend / clicks if clicks > 0 else 0.0
        cpa = spend / td_rev if td_rev > 0 else 0.0 
        
        efficiency_results.append({"channel": ch, "cpc": round(cpc, 2), "cpa": round(cpa, 2)})
        
    eff_df = pd.DataFrame(efficiency_results)
    return attr_metrics, eff_df
