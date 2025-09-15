import logging

from sqlalchemy.exc import IntegrityError

from app.src.core.config import get_settings
from app.src.horoscope.service import HoroscopeService
from app.workers.async_message_worker import SimpleWorker
from app.src.birthprofile.service import BirthProfileService
from app.src.astroprofile.service import AstroProfileService

logger = logging.getLogger(__name__)
settings = get_settings()


async def handle_horoscope(data, session_maker, publisher):
    birth_id = data["birth_id"]
    print(
        f"Got birth_id {birth_id} along with astro profile, generating today's horoscope..."
    )

    async with session_maker() as session:
        try:
            birth_profile = await BirthProfileService(session).get_birth_profile(
                birth_id
            )
            astro_profile = await AstroProfileService(session).get_astro_profile(
                birth_id
            )

            horoscope = await HoroscopeService(session).set_horoscope(
                birth_id, birth_profile, astro_profile
            )

            print(f"horoscope {horoscope} saved for birth_id: {birth_id}")
            logger.info(
                "horoscope generated",
                extra={
                    "extra_info": {
                        "horoscope": str(horoscope),
                        "birth_id": str(birth_id),
                    }
                },
            )

            # publish to message delivery topic to fetch by whatsapp delivery sub
            publisher.publish(
                settings.topic_message_delivery,
                {"birth_id": str(birth_id), "type": "horoscope"},
            )

        except IntegrityError as e:
            # Likely duplicate or unique constraint violation from concurrent processing.
            # Treat as success to avoid redelivery loop.
            logger.info(
                "astro_profile: already exists or race detected for birth_id=%s; treating as done. err=%s",
                birth_id,
                e,
            )
            return  # Will ack

        except (KeyError, ValueError, TypeError) as e:
            # Payload or data-shape issue; do not retry.
            logger.warning(
                "interpretation: non-retryable error for birth_id=%s; err=%s",
                birth_id,
                e,
                exc_info=True,
            )
            return  # Will ack

        except Exception as e:
            # Unknown/transient issue; let the worker nack to allow retry.
            logger.error(
                "interpretation: transient error for birth_id=%s; will retry. err=%s",
                birth_id,
                e,
                exc_info=True,
            )
            raise


if __name__ == "__main__":
    SimpleWorker(
        subscription=settings.sub_horoscope,
        handler=handle_horoscope,
        max_concurrency=1,
    ).start()
