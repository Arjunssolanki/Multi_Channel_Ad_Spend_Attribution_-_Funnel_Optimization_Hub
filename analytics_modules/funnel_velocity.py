import pandas as pd

def calculate_funnel_and_velocity(click_df):
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

    final_velocity_cart = round(float(pd.Series(avg_time_to_cart).fillna(0.0).iloc[0]), 2)
    final_velocity_payment = round(float(pd.Series(avg_time_to_payment).fillna(0.0).iloc[0]), 2)

    funnel_data = pd.DataFrame([
        {"stage_name": "Stage 1: Landing Page", "session_count": total_landing, "conversion_rate": 100.0, "dropoff_rate": 0.0, "avg_velocity_to_cart": final_velocity_cart, "avg_velocity_to_payment": final_velocity_payment},
        {"stage_name": "Stage 2: Cart Additions", "session_count": total_cart, "conversion_rate": round(c_conv, 2), "dropoff_rate": round(100 - c_conv, 2), "avg_velocity_to_cart": final_velocity_cart, "avg_velocity_to_payment": final_velocity_payment},
        {"stage_name": "Stage 3: Payment Confirmation", "session_count": total_payment, "conversion_rate": round(p_conv, 2), "dropoff_rate": round(100 - p_conv, 2), "avg_velocity_to_cart": final_velocity_cart, "avg_velocity_to_payment": final_velocity_payment}
    ])
    
    return funnel_data, total_landing, c_conv, p_conv, overall_conv, final_velocity_cart, final_velocity_payment, landing, cart, payment
