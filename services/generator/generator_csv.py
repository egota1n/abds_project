from __future__ import annotations

import json
import random
import csv
from datetime import datetime, timezone
from faker import Faker

fake = Faker()
random.seed(42)

TOTAL_EVENTS = 200_000
OUT_FILE = "data/events.csv"

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
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session_id": f"session-{random.randint(1, 50_000)}",
        "user_id": random.randint(1, 200_000),
        "url": random.choice(URLS),
        "referrer": random.choice(REFS),
        "device_type": random.choice(DEVICE_TYPES),
        "user_agent": fake.user_agent(),
        "ip": fake.ipv4_public(),
        "payload_json": json.dumps(payload),
    }


def main():
    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "type",
                "created_at",
                "session_id",
                "user_id",
                "url",
                "referrer",
                "device_type",
                "user_agent",
                "ip",
                "payload_json",
            ],
        )
        writer.writeheader()

        for i in range(TOTAL_EVENTS):
            writer.writerow(build_event())

            if i and i % 10_000 == 0:
                print(f"generated {i} events")

    print(f"CSV generated: {OUT_FILE} ({TOTAL_EVENTS} events)")


if __name__ == "__main__":
    main()