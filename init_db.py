import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("DB_HOST")
port = int(os.getenv("DB_PORT", 3306))
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database_name = os.getenv("DB_NAME")

connection = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=password
)

try:
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name};")
    connection.select_db(database_name)
    
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS marketing_spend_logs (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                campaign_id VARCHAR(50),
                channel VARCHAR(30),
                spend_date DATE,
                ad_spend DECIMAL(10, 2),
                impressions INT,
                clicks INT
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS web_clickstream_logs (
                click_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50),
                session_id VARCHAR(50),
                timestamp DATETIME,
                traffic_source VARCHAR(50),
                page_type VARCHAR(30),
                revenue DECIMAL(10, 2)
            );
        """)
    
    connection.commit()
    print("Database infrastructure and structural schemas successfully verified.")

finally:
    connection.close()
