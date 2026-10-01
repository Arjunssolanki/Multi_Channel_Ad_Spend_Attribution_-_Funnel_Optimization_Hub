import os
import random
import json
import pandas as pd
from datetime import datetime, timedelta

channels = ["Google Ads", "meta ads", "google ads", "Meta Ads", "Affiliate", "AFFILIATE"]
pages = ["landing_page", "cart", "payment_confirmation"]

start_date = datetime(2026, 9, 1)
spend_data = []

for i in range(30):
    current_date = start_date + timedelta(days=i)
    for camp_num, channel in enumerate(random.sample(channels, 3)):
        date_formats = [
            current_date.strftime("%Y-%m-%d"),
            current_date.strftime("%m/%d/%Y"),
            f"{current_date.strftime('%Y.%m.%d')} 00:00:00"
        ]
        spend_data.append({
            "campaign_id": f"CAMP_{100 + camp_num}",
            "channel": channel,
            "spend_date": random.choice(date_formats),
            "ad_spend": round(random.uniform(50.0, 500.0), 2),
            "impressions": random.randint(5000, 50000),
            "clicks": random.randint(100, 2000)
        })

spend_df = pd.DataFrame(spend_data)
spend_df.to_csv("raw_marketing_spend.csv", index=False)

clickstream_logs = []
user_pool = [f"USR_{random.randint(10000, 99999)}" for _ in range(50)]

for user_id in user_pool:
    num_sessions = random.randint(1, 3)
    for s_idx in range(num_sessions):
        session_id = f"SESS_{user_id}_{s_idx}"
        session_start = start_date + timedelta(days=random.randint(0, 28), hours=random.randint(0, 23))
        
        path_length = random.choice([1, 2, 3, 3, 3])
        traffic_source = random.choice(["Google Ads", "Meta Ads", "Affiliate", "Direct"])
        
        for p_idx in range(path_length):
            page = pages[p_idx]
            click_time = session_start + timedelta(minutes=p_idx * random.randint(2, 15))
            
            time_formats = [
                click_time.strftime("%Y-%m-%d %H:%M:%S"),
                click_time.isoformat(),
                click_time.strftime("%d-%m-%Y %H:%M:%S")
            ]
            
            log_entry = {
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": random.choice(time_formats),
                "traffic_source": traffic_source if random.random() > 0.1 else None,
                "page_type": page,
                "revenue": round(random.uniform(20.0, 150.0), 2) if page == "payment_confirmation" else None
            }
            clickstream_logs.append(log_entry)

with open("raw_web_clickstream.json", "w") as f:
    for entry in clickstream_logs:
        f.write(json.dumps(entry) + "\n")

print("Raw source data lake simulation files generated successfully.")
