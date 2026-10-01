import os
import boto3
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

bucket_name = os.getenv("S3_BUCKET_NAME")

files_to_upload = {
    "raw_marketing_spend.csv": "landing/raw_marketing_spend.csv",
    "raw_web_clickstream.json": "landing/raw_web_clickstream.json"
}

for local_file, s3_key in files_to_upload.items():
    if os.path.exists(local_file):
        s3_client.upload_file(local_file, bucket_name, s3_key)
        print(f"Successfully moved {local_file} to cloud path s3://{bucket_name}/{s3_key}")
