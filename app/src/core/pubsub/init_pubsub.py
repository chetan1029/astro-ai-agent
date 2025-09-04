from google.cloud import pubsub_v1
from app.src.core.config import get_settings


def init_pubsub():
    settings = get_settings()
    project_id = settings.pubsub_project_id

    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()

    for topic_name, subscriptions in settings.topic_sub_mapping.items():
        topic_path = publisher.topic_path(project_id, topic_name)

        # Create topic if not exists
        try:
            publisher.get_topic(topic=topic_path)
            print(f"[Pub/Sub] Topic {topic_name} exists")
        except Exception:
            publisher.create_topic(name=topic_path)
            print(f"[Pub/Sub] Created topic {topic_name}")

        # Create subscription if not exists
        for sub_name in subscriptions:
            sub_path = subscriber.subscription_path(project_id, sub_name)

            try:
                subscriber.get_subscription(subscription=sub_path)
                print(f"[Pub/Sub] Subscription {sub_name} exists")
            except Exception:
                subscriber.create_subscription(name=sub_path, topic=topic_path)
                print(f"[Pub/Sub] Created subscription {sub_name}")
