import json
import urllib.request

def lambda_handler(event, context):
    webhook_url = "https://ngrok-free.dev"
    
    payload = {"event_source": "aws_s3_notification", "details": event}
    headers = {"Content-Type": "application/json"}
    
    req = urllib.request.Request(
        webhook_url, 
        data=json.dumps(payload).encode("utf-8"), 
        headers=headers, 
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            return {"statusCode": 200, "body": res_body}
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
