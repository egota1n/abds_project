from __future__ import annotations

import json
import os
import random
import time
from datetime import datetime, timezone
from faker import Faker
import pika

RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")
QUEUE = os.getenv("RABBIT_QUEUE", "clickstream.events")
# Скорость генерации
RATE_PER_SEC = float(os.getenv("RATE_PER_SEC", "20"))

fake = Faker()

URLS = ["/", "/catalog", "/catalog?cat=phones", "/product/123", "/product/456", "/checkout"]
REFS = ["", "https://yandex.ru", "https://ozon.ru", "https://wildberries.ru", "https://avito.ru"]
DEVICE_TYPES = ["desktop", "mobile", "tablet"]
EVENT_TITLES = ["page_view", "product_card", "add_to_cart", "checkout", "promo_click"]
ELEMENTS = ["#buy-button", "#submit-button", ".product-card", ".promo-banner", "#search"]

# Генерация события
def build_event() -> dict:
    etype = "click" if random.random() < 0.35 else "view"

    payload = {
        "event_title": random.choice(EVENT_TITLES),
        "element_id": random.choice(ELEMENTS) if etype == "click" else "",
        "x": random.randint(0, 1200) if etype == "click" else 0,
        "y": random.randint(0, 900) if etype == "click" else 0,
    }

    return {
        "type": etype,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "session_id": f"session-{random.randint(1, 50_000)}",
        "user_id": random.randint(1, 200_000),
        "url": random.choice(URLS),
        "referrer": random.choice(REFS),
        "device_type": random.choice(DEVICE_TYPES),
        "user_agent": fake.user_agent(),
        "ip": fake.ipv4_public(),
        "payload": payload,
    }


# Ожидание RabbitMQ
def wait_for_rabbit(host: str, retries: int = 30, delay: int = 2):
    for i in range(retries):
        try:
            return pika.BlockingConnection(
                pika.ConnectionParameters(host=host, heartbeat=30)
            )
        except pika.exceptions.AMQPConnectionError:
            time.sleep(delay)
    raise RuntimeError("RabbitMQ is not available")

def main():
    connection = wait_for_rabbit(RABBIT_HOST)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE, durable=True)

    sleep_s = 1.0 / max(RATE_PER_SEC, 0.1)

    while True:
        event = build_event()
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE,
            body=json.dumps(event).encode("utf-8"),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        time.sleep(sleep_s)

if __name__ == "__main__":
    main()