from django.core.mail import EmailMessage
from typing import Dict
from rest_framework.response import Response
import threading


class ResponseManager:
    """Utility class that abstracts how we create a DRF response"""

    @staticmethod
    def handle_response(
            data: Dict = None, errors: Dict = None, status: int = 200, message: str = ""
    ) -> Response:
        if data is None:
            data = {}
        if errors is None:
            errors = {}
        if errors:
            return Response({"errors": errors, "message": message}, status=status)
        return Response({"data": data, "message": message}, status=status)


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class EmailManager:
    """
    Utility class that abstracts how we send emails
    """
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], from_email='onboarding@aipidata.com',
            to=[data['to_email']])
        email.content_subtype = "html"
        EmailThread(email).start()
