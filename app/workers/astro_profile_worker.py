import json

from app.src.astroprofile.service import AstroProfileService
from app.src.birthprofile.service import BirthProfileService
from app.src.core.db import get_session_maker
from app.src.core.pubsub.subscriber import PubSubSubscriber
from app.src.core.pubsub.publisher import PubSubPublisher
from app.src.core.config import get_settings

settings = get_settings()
publisher = PubSubPublisher()

session_maker = get_session_maker()

async def process_message(message):
    data = json.loads(message.data.decode("utf-8"))
    birth_id = data["birth_id"]
    print(f"Got new birth_id {birth_id}, generating astro profile...")

    async with session_maker() as session:
        birth_profile = await BirthProfileService(session).get_birth_profile(birth_id)

        astro_profile = await AstroProfileService(session).set_astro_profile(
            birth_profile.id,
            birth_profile.date_of_birth_utc,
            birth_profile.birth_place_latitude,
            birth_profile.birth_place_longitude,
        )

        print(f"Created astro profile {astro_profile}")

        # Chain publish to next topics
        payload = {"birth_id": str(birth_id)}
        publisher.publish(settings.topic_astro_profile, payload)

    message.ack()

if __name__ == "__main__":
    subscriber = PubSubSubscriber(settings.sub_astro_profile)
    subscriber.start(process_message)