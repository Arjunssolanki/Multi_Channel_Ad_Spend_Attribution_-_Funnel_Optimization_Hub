import os
import io
import json
import pymysql
import boto3
import pandas as pd
from fastapi import FastAPI, BackgroundTasks
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION")
    )

def clean_marketing_spend(df):
    df["channel"] = df["channel"].str.strip().str.title()
    df["spend_date"] = pd.to_datetime(df["spend_date"], errors="coerce")
    df = df.dropna(subset=["spend_date"])
    df["spend_date"] = df["spend_date"].dt.date
    return df

def clean_clickstream(df):
    df["traffic_source"] = df["traffic_source"].fillna("Direct").str.strip().str.title()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["revenue"] = pd.to_numeric(df["revenue"]).fillna(0.0)
    return df

def execute_pipeline():
    s3 = get_s3_client()
    bucket = os.getenv("S3_BUCKET_NAME")
    
    try:
        marketing_obj = s3.get_object(Bucket=bucket, Key="landing/raw_marketing_spend.csv")
        marketing_df = pd.read_csv(io.BytesIO(marketing_obj["Body"].read()))
        cleaned_spend = clean_marketing_spend(marketing_df)
        
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE marketing_spend_logs;")
            for _, row in cleaned_spend.iterrows():
                cursor.execute("""
                    INSERT INTO marketing_spend_logs (campaign_id, channel, spend_date, ad_spend, impressions, clicks)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (row["campaign_id"], row["channel"], row["spend_date"], row["ad_spend"], row["impressions"], row["clicks"]))
        connection.commit()
        connection.close()
        print("Cloud marketing records processed.")
        
        clickstream_obj = s3.get_object(Bucket=bucket, Key="landing/raw_web_clickstream.json")
        json_lines = clickstream_obj["Body"].read().decode("utf-8").splitlines()
        clickstream_df = pd.DataFrame([json.loads(line) for line in json_lines])
        cleaned_clicks = clean_clickstream(clickstream_df)
        
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE web_clickstream_logs;")
            for _, row in cleaned_clicks.iterrows():
                cursor.execute("""
                    INSERT INTO web_clickstream_logs (user_id, session_id, timestamp, traffic_source, page_type, revenue)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (row["user_id"], row["session_id"], row["timestamp"], row["traffic_source"], row["page_type"], row["revenue"]))
        connection.commit()
        connection.close()
        print("Cloud clickstream records processed.")
        
        print("Recalculating downstream multi-channel metrics.")
        import attribution_models
        attribution_models.compute_attribution()
        
    except Exception as e:
        print(f"Data stream encountered an interruption: {e}")

@app.post("/webhook/s3-update")
def s3_update_webhook(payload: dict, background_tasks: BackgroundTasks):
    print("Inbound AWS cloud event detected via webhook payload notification.")
    background_tasks.add_task(execute_pipeline)
    return {"status": "event_received", "message": "Pipeline processing scheduled."}
