import requests
import time
from math import *
import boto3


async def notify_partner_webhook(endpoint: str, payload: dict) -> bool:
    """TODO"""
    time.sleep(1)
    print(f"Sending webhook to {endpoint} with ceil={ceil(1.2)}")
    resp = requests.post(endpoint, json=payload)
    _ = boto3
    return resp.status_code == 200
