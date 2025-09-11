import logging

from sqlalchemy.exc import IntegrityError
from twilio.base.exceptions import TwilioRestException

from app.src.birthprofile.service import BirthProfileService
from app.src.core.config import get_settings
from app.src.horoscope.service import HoroscopeService
from app.src.interpretation.service import InterpretationService
from app.src.userprofile.service import UserProfileService
from app.workers.async_message_worker import SimpleWorker
from app.src.whatsapp.service import WhatsAppService

logger = logging.getLogger(__name__)
settings = get_settings()


async def handle_whatsapp_delivery(data, session_maker, publisher):
    birth_id = data["birth_id"]
    type = data["type"]
    print(f"whatsapp delivery recieve birth_id {birth_id}")

    async with session_maker() as session:
        try:
            birth_profile = await BirthProfileService(session).get_birth_profile(
                birth_id
            )
            user_profile = await UserProfileService(session).get_user_profile(
                birth_profile.user_profile_id
            )
            to = user_profile.phone_number
            text = ""

            if type == "interpretation":
                interpretation = await InterpretationService(
                    session
                ).get_interpretation(birth_id)
                text = interpretation.content
            elif type == "horoscope":
                horoscope = await HoroscopeService(session).get_horoscope(birth_id)
                text = horoscope.content

            print(to, text, type)
            whatsapp_service = WhatsAppService.from_settings()
            await whatsapp_service.send_message(to, text)

            logger.info(
                "whatsapp message sent",
                extra={
                    "extra_info": {
                        "to": str(to),
                        "text": str(text),
                    }
                },
            )

        except TwilioRestException as e:
            if e.status == 400:
                logger.warning(
                    "Permanent Twilio error (no retry) for birth_id=%s; err=%s",
                    birth_id,
                    e.msg,
                )
                return  # Do NOT raise → acknowledges and stops retries
            raise  # Other Twilio errors might be transient → allow retry

        except IntegrityError as e:
            # Likely duplicate or unique constraint violation from concurrent processing.
            # Treat as success to avoid redelivery loop.
            logger.info(
                "astro_profile: already exists or race detected for birth_id=%s; treating as done. err=%s",
                birth_id,
                e,
            )
            return

        except (KeyError, ValueError, TypeError) as e:
            # Payload or data-shape issue; do not retry.
            logger.warning(
                "can't send whatsapp message to : non-retryable error for birth_id=%s; err=%s",
                birth_id,
                e,
                exc_info=True,
            )
            return  # Will ack

        except Exception as e:
            # Unknown/transient issue; let the worker nack to allow retry.
            logger.error(
                "can't send whatsapp message: transient error for birth_id=%s; will retry. err=%s",
                birth_id,
                e,
                exc_info=True,
            )
            raise


if __name__ == "__main__":
    SimpleWorker(
        subscription=settings.sub_whatsapp_delivery,
        handler=handle_whatsapp_delivery,
        max_concurrency=1,
    ).start()
