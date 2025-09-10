# import json
#
# from app.src.core.db import get_session_maker
# from app.src.core.pubsub.subscriber import PubSubSubscriber
# from app.src.core.pubsub.publisher import PubSubPublisher
# from app.src.core.config import get_settings
# from app.src.whatsapp.service import WhatsAppService
#
# settings = get_settings()
# publisher = PubSubPublisher()
#
# session_maker = get_session_maker()
#
#
# async def process_message(message):
#     try:
#         data = json.loads(message.data.decode("utf-8"))
#         text = data["text"]
#         to = data["to"]
#
#         print(f"Got new text: {text} for number: {to}")
#
#         whatsapp_service = WhatsAppService.from_settings()
#         await whatsapp_service.send_outgoing_message(to, text)
#
#         print(f"✅ Sent WhatsApp message to {to}")
#         message.ack()
#     except Exception as e:
#         print(f"❌ Failed to send WhatsApp message: {e}")
#         message.nack()  # re-deliver later
#
#
# if __name__ == "__main__":
#     subscriber = PubSubSubscriber(settings.sub_whatsapp_delivery)
#     subscriber.start(process_message)
