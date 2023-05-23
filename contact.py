import smtplib

EMAIL = ""
PWD = ""

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
                to_addrs="",
                msg=f"{self.name}\n{self.email}\n{self.body}\n{self.subject}"
            )