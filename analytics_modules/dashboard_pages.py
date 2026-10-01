import pandas as pd

def calculate_bi_dashboard_pages(click_df, attr_metrics, landing, cart, payment):
    # 📉 Page 2 Table: Granular Channel Cohort Funnel Matrix
    cohort_funnel = click_df.merge(landing, on="session_id", how="left")
    cohort_funnel = cohort_funnel.merge(cart, on="session_id", how="left")
    cohort_funnel = cohort_funnel.merge(payment, on="session_id", how="left")
    
    channel_cohorts = []
    for ch in click_df["traffic_source"].unique():
        ch_data = cohort_funnel[cohort_funnel["traffic_source"] == ch]
        ch_landing = ch_data["session_id"].nunique()
        ch_cart = ch_data[ch_data["cart_time"].notna()]["session_id"].nunique()
        ch_pay = ch_data[ch_data["cart_time"].notna() & ch_data["payment_time"].notna()]["session_id"].nunique()
        
        channel_cohorts.append({
            "traffic_channel": ch, 
            "stage_1_visits": ch_landing, 
            "stage_2_carts": ch_cart, 
            "stage_3_payments": ch_pay
        })
        
    cohort_df = pd.DataFrame(channel_cohorts)

    # 💰 Page 3 Table: Strategic ROI & Budget Reallocation Optimization Model
    reallocation_model = []
    for _, row in attr_metrics.iterrows():
        ch = row["channel"]
        spend = float(row["ad_spend"])
        td_rev = float(row["time_decay_rev"])
        roas = td_rev / spend if spend > 0 else 0.0
        
        recommended_action = "Maintain"
        budget_shift_pct = 0.0
        
        if roas > 0.15:
            recommended_action = "Scale Investment (Aggressive)"
            budget_shift_pct = 25.0
        elif roas < 0.05:
            recommended_action = "Reduce Allocation (Drain Hazard)"
            budget_shift_pct = -30.0
            
        reallocation_model.append({
            "channel": ch,
            "current_roas": round(roas, 4),
            "recommended_action": recommended_action,
            "budget_shift_percentage": budget_shift_pct
        })
        
    realloc_df = pd.DataFrame(reallocation_model)
    return cohort_df, realloc_df
