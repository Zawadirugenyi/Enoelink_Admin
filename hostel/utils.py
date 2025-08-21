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




from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors
import os
import random

def create_default_rvp(self, tenant_name):
        # Use tenant_name directly without encoding it
        tenant_name = tenant_name if tenant_name else "Unknown Tenant"

        # Create a PDF with event details
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        content = []

        # Teal Color Scheme
        teal = colors.HexColor('#008080')
        light_teal = colors.HexColor('#20B2AA')
        dark_teal = colors.HexColor('#004d40')
        light_background = colors.HexColor('#e0f2f1')
        teal_text = colors.HexColor('#004d40')

        # Styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title_style.textColor = teal
        body_style = styles['BodyText']
        body_style.textColor = teal_text
        conclusion_style = ParagraphStyle(
            name='ConclusionStyle',
            fontSize=10,
            alignment=1,
            spaceAfter=20,
            textColor=teal_text
        )

        # Title
        content.append(Paragraph(f"Event Ticket: {self.title}", title_style))

        # Serial Number
        serial_number = f"Serial Number: {random.randint(100000, 999999)}"
        content.append(Paragraph(serial_number, body_style))

        # Event and Tenant Details
        details = [
            ["Tenant Name:", tenant_name],  # Use tenant_name directly
            ["Event Title:", self.title],
            ["Date:", self.date.strftime("%A, %B %d, %Y")],
            ["Location:", self.location],
            ["Description:", Paragraph(self.description, body_style)],
        ]

        # Table with adjusted column width for the description
        table = Table(details, colWidths=[120, 440])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), dark_teal),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), light_background),
            ('GRID', (0, 0), (-1, -1), 1, dark_teal),
        ]))

        content.append(table)

        # Conclusion
        content.append(Paragraph("Thank you for joining us. We look forward to seeing you at the event!", conclusion_style))

        # Build PDF
        doc.build(content)
        buffer.seek(0)


        # Create a unique filename for the PDF, using tenant_name directly
        file_name = f"{self.title.replace(' ', '_')}_{tenant_name.replace(' ', '_')}_{random.randint(1000, 9999)}.pdf"
        return ContentFile(buffer.read(), file_name)
