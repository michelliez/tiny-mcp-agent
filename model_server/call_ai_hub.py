import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

def encode_b64(text: str) -> str:
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')


def call_ai_hub(system_prompt: str, user_prompt: str) -> str:
    url = f"{os.getenv('AI_HUB_URL')}/generative"
    payload = {
        'ad_object_id': os.getenv('AD_OBJECT_ID'),
        'context': encode_b64(system_prompt),
        'models': ['claude-sonnet-4.6'],
        'prompt': encode_b64(user_prompt)
    }
    headers = {
        "X-API-Key": os.getenv("AI_HUB_API_KEY"),  
        "Content-Type": "application/json"  
    }
    response = requests.post(url, json=payload, headers=headers, timeout=60)
    response.raise_for_status()

    data = response.json()
    if data.get('has_error'):
        raise RuntimeError(data.get('error'))
    
    responses = data['data']['generative_responses']
    first = responses[0]
    if first.get('has_error'):
        raise RuntimeError(first.get('response'))
    
    return first['response']
