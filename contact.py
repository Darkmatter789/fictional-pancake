import os
import requests
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

TO_EMAIL = "terrig.rca@gmail.com"
URL = "https://api.elasticemail.com/v2/email/send"
API_KEY = os.environ.get("API_KEY")

class Contact:

    def __init__(self, name, email, body):
        self.name = name
        self.email = email
        self.body = body


    def send_message(self):
        try:
            self._send_email()
            logging.info('Email sent successfully!')
        except Exception as e:
            logging.info('Failed to send email:', e)
        


    def _send_email(self):
        data = {
            "apikey": API_KEY,
            "subject": "Subject: Contact Form Submission",
            "from": self.email,
            "fromName": self.name,
            "to": TO_EMAIL,
            "bodyText": self.body
        }
        response = requests.post(URL, data=data)
        if response.status_code == 200:
            return True
        else:
            return False
      


    def send_reset_link(user_email, user_id):
        link = f"http://riversidechristianacademy.org/reset/{user_id}"
        data = {
            "apikey": API_KEY,
            "subject": "Contact Form Submission",
            "from": "RiverSide_Admin_Password_Reset",
            "to": user_email,
            "bodyText": f"Reset your password {link}"
        }
        response = requests.post(URL, data=data)
        if response.status_code == 200:
            return True
        else:
            return False
        
