import smtplib
import os

EMAIL = os.environ.get('EMAIL')
PWD = os.environ.get('PWD')
TO_EMAIL = os.environ.get('FROM_EMAIL')

class Contact:

    def __init__(self, name, email, body, subject=None):
        self.name = name
        self.email = email
        self.subject = subject
        self.body = body


    def send_message(self):
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=EMAIL, password=PWD)
            connection.sendmail(
                from_addr=EMAIL,
                to_addrs=TO_EMAIL,
                msg=f"{self.name}\n{self.email}\n{self.body}\n{self.subject}"
            )


    def send_reset_link(user_email, user_id):
        link = f"http://riversidechristianacademy.org/reset/{user_id}"
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=EMAIL, password=PWD)
            connection.sendmail(
                from_addr=EMAIL,
                to_addrs=user_email,
                msg=f"Reset password for {user_email}\n{link}"
            )
