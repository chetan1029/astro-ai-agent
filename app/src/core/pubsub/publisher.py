import json
import logging
from google.cloud import pubsub_v1
from app.src.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PubSubPublisher:
    def __init__(self):
        self.publisher = pubsub_v1.PublisherClient()
        self.project_id = settings.pubsub_project_id

    def publish(self, topic: str, message: dict) -> str:
        topic_path = self.publisher.topic_path(self.project_id, topic)
        data = json.dumps(message).encode("utf-8")
        future = self.publisher.publish(topic_path, data)
        msg_id = future.result()
        logger.info(f"Published to {topic}: {message}, msg_id={msg_id}")
        return msg_id
