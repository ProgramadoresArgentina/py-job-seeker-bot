import sendgrid
from sendgrid.helpers.mail import Mail
import json
import os
from dotenv import load_dotenv

load_dotenv()

sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))

try:
    segment_id = "f21460e4-193d-4945-8381-aa6ae4544f35"
    response = sg.client.marketing.segments._(segment_id).get()
    response_data = json.loads(response.body)
    email_list = [contact['email'] for contact in response_data.get('contacts_sample', [])]

    for email in email_list:
        print(email)

except Exception as e:
    print(f"An error occurred: {str(e)}")
