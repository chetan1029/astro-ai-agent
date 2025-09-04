import json

from app.src.astroprofile.service import AstroProfileService
from app.src.birthprofile.service import BirthProfileService
from app.src.core.db import get_session_maker
from app.src.core.pubsub.subscriber import PubSubSubscriber
from app.src.core.pubsub.publisher import PubSubPublisher
from app.src.core.config import get_settings
from app.src.horoscope.service import HoroscopeService

settings = get_settings()
publisher = PubSubPublisher()

session_maker = get_session_maker()


async def process_message(message):
    data = json.loads(message.data.decode("utf-8"))
    birth_id = data["birth_id"]
    print(f"Got birth_id {birth_id} along with astro profile, generating today's horoscope...")

    async with session_maker() as session:
        birth_profile = await BirthProfileService(session).get_birth_profile(birth_id)

        astro_profile = await AstroProfileService(session).get_astro_profile(birth_id)

        horoscope = await HoroscopeService(session).set_horoscope(birth_id, birth_profile, astro_profile)

        print(f"horoscope is {horoscope}")

    message.ack()


if __name__ == "__main__":
    subscriber = PubSubSubscriber(settings.sub_horoscope)
    subscriber.start(process_message)