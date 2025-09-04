import json

from app.src.astroprofile.service import AstroProfileService
from app.src.birthprofile.service import BirthProfileService
from app.src.core.db import get_session_maker
from app.src.core.pubsub.subscriber import PubSubSubscriber
from app.src.core.pubsub.publisher import PubSubPublisher
from app.src.core.config import get_settings
from app.src.interpretation.service import InterpretationService

settings = get_settings()
publisher = PubSubPublisher()

session_maker = get_session_maker()

async def process_message(message):
    data = json.loads(message.data.decode("utf-8"))
    birth_id = data["birth_id"]
    print(f"Got birth_id {birth_id} along with astro profile, generating profile interpretation...")

    async with session_maker() as session:
        birth_profile = await BirthProfileService(session).get_birth_profile(birth_id)

        astro_profile = await AstroProfileService(session).get_astro_profile(birth_id)

        interpretation = await InterpretationService(session).set_interpretation(birth_id, birth_profile, astro_profile)

        print(f"interpretation is {interpretation}")

    message.ack()

if __name__ == "__main__":
    subscriber = PubSubSubscriber(settings.sub_interpretation)
    subscriber.start(process_message)