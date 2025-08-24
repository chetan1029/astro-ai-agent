import requests
from app.src.core.config import get_settings
from .base import MessagingProvider

class WhatsAppCloudProvider(MessagingProvider):
    def __init__(self):
        settings = get_settings()
        self.access_token = settings.whatsapp_access_token
        self.phone_number_id = settings.whatsapp_phone_number_id

    def send_message(self, to: str, message: str) -> None:
        url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        r = requests.post(url, headers=headers, json=payload)
        print("WhatsApp send response:", r.json())

    def parse_incoming(self, data: dict) -> tuple[str, str, str]:
        """
        Parse incoming WhatsApp Cloud API data.
        Returns: (from_number, text, contact_name)
        """
        change = data["entry"][0]["changes"][0]
        value = change["value"]

        msg = value["messages"][0]
        from_number = msg["from"]
        text = msg.get("text", {}).get("body", "")
        contact_name = value["contacts"][0]["profile"]["name"]

        return from_number, text, contact_name
