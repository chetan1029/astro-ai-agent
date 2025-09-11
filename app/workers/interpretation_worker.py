import logging
from sqlalchemy.exc import IntegrityError
from app.src.core.config import get_settings
from app.workers.async_message_worker import SimpleWorker
from app.src.astroprofile.service import AstroProfileService
from app.src.birthprofile.service import BirthProfileService
from app.src.interpretation.service import InterpretationService

logger = logging.getLogger(__name__)
settings = get_settings()


async def handle_interpretation(data, session_maker, publisher):
    birth_id = data["birth_id"]
    logger.info("Generating interpretation for birth_id=%s", birth_id)

    async with session_maker() as session:
        try:
            birth_profile = await BirthProfileService(session).get_birth_profile(
                birth_id
            )
            astro_profile = await AstroProfileService(session).get_astro_profile(
                birth_id
            )

            interpretation = await InterpretationService(session).set_interpretation(
                birth_id, birth_profile, astro_profile
            )

            print(f"Interpretation {interpretation} saved for birth_id: {birth_id}")
            logger.info(
                "Interpretation generated",
                extra={"extra_info": {"interpretation": str(interpretation), "birth_id": str(birth_id)}},
            )

            # publish to message delivery topic to fetch by whatsapp delivery sub
            publisher.publish(settings.topic_message_delivery, {"birth_id": str(birth_id), "type": "interpretation"})

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
        subscription=settings.sub_interpretation,
        handler=handle_interpretation,
        max_concurrency=1,
    ).start()
