import logging
from app.src.birthprofile.service import BirthProfileService
from app.src.core.config import get_settings
from app.src.userprofile.service import UserProfileService
from app.src.core.utils import normalize_phone_number
from app.src.whatsapp.dependencies import get_messaging_provider
from app.src.whatsapp.exceptions import WhatsappError
from app.src.whatsapp.logic import parse_message_to_birth_profile
from app.src.whatsapp.providers.base import MessagingProvider

logger = logging.getLogger(__name__)


class WhatsAppService:
    def __init__(self, session, messaging: MessagingProvider):
        self.session = session
        self.messaging = messaging

    @classmethod
    def from_settings(cls, session=None):
        """Factory method to create service outside FastAPI (e.g., in workers)."""
        settings = get_settings()
        messaging = get_messaging_provider(settings.whatsapp_provider)
        return cls(session, messaging)

    async def handle_incoming_message(
        self, from_number: str, text: str, contact_name: str
    ) -> str:
        try:
            birth_profile = parse_message_to_birth_profile(text)

            # Link to user profile
            user_profile = await UserProfileService(self.session).get_or_set_by_phone(
                normalize_phone_number(from_number)
            )
            birth_profile.user_profile_id = user_profile.id

            # Save birth profile
            result = await BirthProfileService(self.session).set_birth_profile(
                birth_profile
            )

            response_text = f"✅ Profile saved for {contact_name} {birth_profile.name} with id {result.id}"
            self.messaging.send_message(from_number, response_text)

            logger.info(
                "Birth profile created via WhatsApp",
                extra={"extra_info": birth_profile.dict()},
            )
            return response_text

        except Exception as e:
            logger.error("Error handling WhatsApp message", exc_info=e)
            if from_number:
                self.messaging.send_message(
                    from_number,
                    "⚠️ Sorry, could not process your message. Please use format:\n\n"
                    "Name, DOB (YYYY-MM-DD HH:MM), Place, Relationship",
                )
            raise WhatsappError("Failed to process message") from e

    def send_outgoing_message(self, to: str, text: str):
        """Send message from workers (no DB needed)."""
        self.messaging.send_message(to, text)
