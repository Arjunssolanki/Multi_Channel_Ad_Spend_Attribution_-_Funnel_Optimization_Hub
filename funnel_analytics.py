import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_clickstream_data():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", 3306)
    database = os.getenv("DB_NAME")
    
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")
    query = "SELECT user_id, session_id, timestamp, page_type FROM web_clickstream_logs;"
    return pd.read_sql(query, engine)

def calculate_funnel_velocity():
    df = get_clickstream_data()
    
    if df.empty:
        print("Awaiting raw transactional records in database tables.")
        return
        
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    landing = df[df["page_type"] == "landing_page"].groupby("session_id")["timestamp"].min().reset_index()
    landing.rename(columns={"timestamp": "landing_time"}, inplace=True)
    
    cart = df[df["page_type"] == "cart"].groupby("session_id")["timestamp"].min().reset_index()
    cart.rename(columns={"timestamp": "cart_time"}, inplace=True)
    
    payment = df[df["page_type"] == "payment_confirmation"].groupby("session_id")["timestamp"].min().reset_index()
    payment.rename(columns={"timestamp": "payment_time"}, inplace=True)
    
    funnel = landing.merge(cart, on="session_id", how="left")
    funnel = funnel.merge(payment, on="session_id", how="left")
    
    total_landing = len(funnel)
    
    funnel_with_cart = funnel[funnel["cart_time"].notna()]
    total_cart = len(funnel_with_cart)
    
    funnel_with_payment = funnel_with_cart[funnel_with_cart["payment_time"].notna()]
    total_payment = len(funnel_with_payment)
    
    cart_conversion = (total_cart / total_landing) * 100 if total_landing > 0 else 0
    cart_dropoff = 100 - cart_conversion
    
    payment_conversion = (total_payment / total_cart) * 100 if total_cart > 0 else 0
    payment_dropoff = 100 - payment_conversion
    
    overall_conversion = (total_payment / total_landing) * 100 if total_landing > 0 else 0
    
    funnel["landing_to_cart_mins"] = (funnel["cart_time"] - funnel["landing_time"]).dt.total_seconds() / 60.0
    funnel["cart_to_payment_mins"] = (funnel["payment_time"] - funnel["cart_time"]).dt.total_seconds() / 60.0
    
    avg_time_to_cart = funnel["landing_to_cart_mins"].mean()
    avg_time_to_payment = funnel["cart_to_payment_mins"].mean()
    
    print("\n======================= DIGITAL MARKETING CONVERSION FUNNEL =======================")
    print(f"Stage 1: Landing Page Visits   : {total_landing} sessions")
    print(f"Stage 2: Added Items to Cart   : {total_cart} sessions ({cart_conversion:.2f}% conversion / {cart_dropoff:.2f}% drop-off)")
    print(f"Stage 3: Payment Confirmations : {total_payment} sessions ({payment_conversion:.2f}% conversion / {payment_dropoff:.2f}% drop-off)")
    print(f"Overall Funnel Conversion Rate : {overall_conversion:.2f}%")
    print("===================================================================================")
    
    print("\n========================= USER JOURNEY FUNNEL VELOCITY =========================")
    print(f"Average Velocity (Landing Page ──► Cart)        : {avg_time_to_cart:.2f} minutes")
    print(f"Average Velocity (Cart ──► Payment Confirmation): {avg_time_to_payment:.2f} minutes")
    print("===================================================================================\n")

if __name__ == "__main__":
    calculate_funnel_velocity()
