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

# dashboard/utils.py
import matplotlib.pyplot as plt
import io
import base64

def get_graph():
    # Generate your graph using Matplotlib
    plt.figure(figsize=(10, 5))
    plt.plot([1, 2, 3], [4, 5, 6])  # Replace with your data
    plt.title('Hostel Views Graph')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    
    # Save the plot to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Encode the image in base64 and return it as a data URL
    graph_image = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{graph_image}"

def get_booking_graph():
    # Generate your graph using Matplotlib
    plt.figure(figsize=(10, 5))
    plt.bar(['Hostel A', 'Hostel B'], [10, 15])  # Replace with your data
    plt.title('Hostel Bookings Graph')
    plt.xlabel('Hostel')
    plt.ylabel('Bookings')
    
    # Save the plot to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Encode the image in base64 and return it as a data URL
    booking_graph_image = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{booking_graph_image}"

# utils.py
from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa

def generate_pdf_from_html(html_content):
    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html_content.encode("UTF-8")), dest=result)
    if pdf.err:
        return None
    return result.getvalue()
