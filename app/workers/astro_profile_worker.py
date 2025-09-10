import logging

from sqlalchemy.exc import IntegrityError

from app.src.core.config import get_settings
from app.workers.async_message_worker import SimpleWorker
from app.src.birthprofile.service import BirthProfileService
from app.src.astroprofile.service import AstroProfileService

logger = logging.getLogger(__name__)
settings = get_settings()


async def handle_astro_profile(data, session_maker, publisher):
    birth_id = data.get("birth_id")
    if not birth_id:
        logger.warning(
            "astro_profile: missing birth_id in payload; acking and skipping. payload=%r",
            data,
        )
        return  # Will ack

    async with session_maker() as session:
        try:
            # Load birth profile
            birth_profile = await BirthProfileService(session).get_birth_profile(
                birth_id
            )

            # Create/update astro profile from birth profile
            await AstroProfileService(session).set_astro_profile(
                birth_id,
                birth_profile.date_of_birth_utc,
                birth_profile.birth_place_latitude,
                birth_profile.birth_place_longitude,
            )

            logger.info(
                "Astro profile generated",
                extra={"extra_info": {"birth_profile_id": str(birth_id)}},
            )

            # Optional chaining: make sure this is NOT the same topic as sub_astro_profile
            publisher.publish(settings.topic_astro_profile, {"birth_id": str(birth_id)})

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
                "astro_profile: non-retryable error for birth_id=%s; err=%s",
                birth_id,
                e,
                exc_info=True,
            )
            return  # Will ack

        except Exception as e:
            # Unknown/transient issue; let the worker nack to allow retry.
            logger.error(
                "astro_profile: transient error for birth_id=%s; will retry. err=%s",
                birth_id,
                e,
                exc_info=True,
            )
            raise


if __name__ == "__main__":
    SimpleWorker(
        subscription=settings.sub_astro_profile,
        handler=handle_astro_profile,
        max_concurrency=1,
    ).start()
