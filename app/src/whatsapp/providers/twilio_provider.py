from twilio.rest import Client
from .base import MessagingProvider
from app.src.core.config import get_settings


class TwilioProvider(MessagingProvider):
    def __init__(self):
        settings = get_settings()
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self.from_number = settings.twilio_whatsapp_number  # e.g. whatsapp:+14155238886

    def send_message(self, to: str, message: str) -> None:
        if to.startswith("whatsapp:") and not to.startswith("whatsapp:+"):
            to = to.replace("whatsapp: ", "whatsapp:+")

        response = self.client.messages.create(
            from_=self.from_number, body=message, to=to
        )
        print("Twilio send response:", response.sid)

    def parse_incoming(self, data: dict) -> tuple[str, str, str]:
        """
        Parse incoming Twilio webhook data.
        Returns: (from_number, text, contact_name)
        """
        from_number = data.get("From")  # e.g. "whatsapp:+919876543210"
        text = data.get("Body", "")
        contact_name = from_number  # Twilio does not provide name
        return from_number, text, contact_name
