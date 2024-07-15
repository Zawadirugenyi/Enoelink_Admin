# utils.py
import requests
from django.conf import settings
import base64
from datetime import datetime

def get_access_token():
    consumer_key = settings.SAFARICOM_CONSUMER_KEY
    consumer_secret = settings.SAFARICOM_CONSUMER_SECRET
    api_url = settings.SAFARICOM_AUTH_URL

    response = requests.get(api_url, auth=(consumer_key, consumer_secret))
    access_token = response.json().get('access_token')

    return access_token

def lipa_na_mpesa_online(phone_number, amount, account_reference, transaction_desc):
    access_token = get_access_token()
    api_url = settings.SAFARICOM_LIPA_NA_MPESA_ONLINE_URL
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f'{settings.SAFARICOM_SHORTCODE}{settings.SAFARICOM_PASSKEY}{timestamp}'.encode()).decode('utf-8')
    payload = {
        "BusinessShortCode": settings.SAFARICOM_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": settings.SAFARICOM_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.SAFARICOM_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

