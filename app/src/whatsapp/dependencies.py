from app.src.whatsapp.providers.twilio_provider import TwilioProvider
from app.src.whatsapp.providers.cloud_provider import WhatsAppCloudProvider
from app.src.whatsapp.providers.base import MessagingProvider
from app.src.core.config import get_settings


def get_messaging_provider() -> MessagingProvider:
    provider = get_settings().whatsapp_provider
    if provider == "cloud":
        return WhatsAppCloudProvider()
    return TwilioProvider()
