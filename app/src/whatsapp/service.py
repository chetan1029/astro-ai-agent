import logging

from twilio.base.exceptions import TwilioRestException

from app.src.birthprofile.exceptions import BirthProfileAlreadyExistsError
from app.src.birthprofile.service import BirthProfileService
from app.src.userprofile.service import UserProfileService
from app.src.core.utils import normalize_phone_number
from app.src.whatsapp.dependencies import get_messaging_provider
from app.src.whatsapp.exceptions import WhatsappError
from app.src.whatsapp.logic import parse_message_to_birth_profile
from app.src.whatsapp.providers.base import MessagingProvider

logger = logging.getLogger(__name__)
MAX_WHATSAPP_LENGTH = 1600


class WhatsAppService:
    def __init__(self, session, messaging: MessagingProvider):
        self.session = session
        self.messaging = messaging

    @classmethod
    def from_settings(cls, session=None):
        """Factory method to create service outside FastAPI (e.g., in workers)."""
        messaging = get_messaging_provider()
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

            response_text = (
                f"✅ ✨ Thanks, {birth_profile.name}! "
                f"\n We’ve received your details and are now preparing your personalized interpretation and horoscope. "
                f"\n This may take a moment, but we’ll send your insights shortly—sit back and relax while we get everything ready for you. 🌟"
            )
            await self.send_message(from_number, response_text)

            logger.info(
                "Birth profile created via WhatsApp",
                extra={"extra_info": birth_profile.dict(), "birth_id": result.id},
            )
            return response_text

        except BirthProfileAlreadyExistsError as e:
            logger.error("Birth profile already exists", exc_info=e)
            if from_number:
                await self.send_message(
                    from_number,
                    "You are already registered with us.",
                )
            raise

        except Exception as e:
            logger.error("Error handling WhatsApp message", exc_info=e)
            if from_number:
                await self.send_message(
                    from_number,
                    "⚠️ Sorry, could not process your message. Please use format:\n\n"
                    "Name, DOB (YYYY-MM-DD HH:MM), Place, Relationship",
                )
            raise WhatsappError("Failed to process message") from e

    async def send_message(self, to: str, text: str):
        """Send message from workers (no DB needed)."""
        if not to.startswith("whatsapp:"):
            to = f"whatsapp:{to}"
        if len(text) > MAX_WHATSAPP_LENGTH:
            logger.warning(
                "Message too long (%d chars). Truncating to %d.",
                len(text),
                MAX_WHATSAPP_LENGTH,
            )
            text = text[:MAX_WHATSAPP_LENGTH]
        try:
            self.messaging.send_message(to, text)
            logger.info("WhatsApp message sent to %s", to)
        except TwilioRestException as e:
            if e.status == 400:
                # Permanent error → don’t retry
                logger.error(
                    "Permanent Twilio error for %s: %s", to, e.msg, exc_info=True
                )
                return
            raise
