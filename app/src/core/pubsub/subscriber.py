import logging
from google.cloud import pubsub_v1
from app.src.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PubSubSubscriber:
    def __init__(self, subscription: str):
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(
            settings.pubsub_project_id, subscription
        )

    def start(self, callback):
        """Start listening with a synchronous callback."""
        logger.info(f"Listening on {self.subscription_path}...")
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path, callback=callback
        )
        try:
            streaming_pull_future.result()  # blocks, keeps running
        except Exception as e:
            logger.error(f"Subscriber stopped with error: {e}")
        finally:
            self.subscriber.close()
