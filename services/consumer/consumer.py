from __future__ import annotations

import json
import os
import time
import pika
import httpx

# RabbitMQ
RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")
QUEUE = os.getenv("RABBIT_QUEUE", "clickstream.events")

# HTTP API
API_URL = os.getenv("API_URL", "http://api:4015/events")

# Batch-настройки
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "200"))
FLUSH_INTERVAL_SEC = float(os.getenv("FLUSH_INTERVAL_SEC", "1.0"))


# Ожидание доступности RabbitMQ
def wait_for_rabbit(host: str, retries: int = 30, delay: int = 2):
    for i in range(retries):
        try:
            return pika.BlockingConnection(
                pika.ConnectionParameters(host=host, heartbeat=30)
            )
        except pika.exceptions.AMQPConnectionError:
            print(f"RabbitMQ not ready, retry {i + 1}/{retries}")
            time.sleep(delay)
    raise RuntimeError("RabbitMQ is not available")


def main(): # pragma: no cover
    # Подключение к RabbitMQ
    conn = wait_for_rabbit(RABBIT_HOST)
    ch = conn.channel()
    ch.queue_declare(queue=QUEUE, durable=True)
    ch.basic_qos(prefetch_count=BATCH_SIZE)

    batch: list[dict] = []
    last_flush = time.time()

    client = httpx.Client(timeout=10.0)

    # Отправка событий в API
    def flush():
        nonlocal batch, last_flush
        if not batch:
            return

        resp = client.post(API_URL, json=batch)
        resp.raise_for_status()

        batch = []
        last_flush = time.time()

    # Обработка сообщений из очереди
    def callback(channel, method, properties, body):
        nonlocal batch, last_flush

        event = json.loads(body.decode("utf-8"))
        batch.append(event)

        now = time.time()
        if len(batch) >= BATCH_SIZE or (now - last_flush) >= FLUSH_INTERVAL_SEC:
            flush()

        channel.basic_ack(delivery_tag=method.delivery_tag)

    ch.basic_consume(queue=QUEUE, on_message_callback=callback)

    try:
        ch.start_consuming()
    finally:
        client.close()
        conn.close()


if __name__ == "__main__":
    main()