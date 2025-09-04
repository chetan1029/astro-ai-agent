import json
import logging
import asyncio
import sys
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

    def start(self, async_callback):
        """Start listening with an async callback."""

        def _wrapper(message: pubsub_v1.subscriber.message.Message):
            try:
                asyncio.run(async_callback(message))
            except Exception as e:
                logger.error(f"Error in subscriber callback: {e}")
                message.nack()

        logger.info(f"Listening on {self.subscription_path}...")
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path, callback=_wrapper
        )

        try:
            streaming_pull_future.result()  # blocks forever
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            logger.info("Stopped listening.")
            sys.exit(0)
