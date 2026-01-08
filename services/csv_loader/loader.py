from __future__ import annotations

import os
import json
import pandas as pd
import httpx

# Пути и настройки
CSV_PATH = os.getenv("CSV_PATH", "/data/events.csv")
API_URL = os.getenv("API_URL", "http://api:4015/events")
CHUNK = int(os.getenv("CHUNK", "500"))

# Безопасное приведение к строке
def safe_str(v: object) -> str:
    if v is None or pd.isna(v):
        return ""
    return str(v)

# Безопасное приведение к int
def safe_int(v: object, default: int = 0) -> int:
    if v is None or pd.isna(v):
        return default
    try:
        return int(v)
    except Exception:
        return default

# Парсинг JSON payload из CSV
def safe_payload(v: object) -> dict:
    if v is None or pd.isna(v):
        return {}
    try:
        parsed = json.loads(v)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def main():
    df = pd.read_csv(CSV_PATH)

    with httpx.Client(timeout=30.0) as client:
        for i in range(0, len(df), CHUNK):
            chunk = df.iloc[i:i + CHUNK]
            events = []

            for _, row in chunk.iterrows():
                events.append({
                    "type": safe_str(row.get("type")),
                    "created_at": safe_str(row.get("created_at")),
                    "session_id": safe_str(row.get("session_id")),
                    "user_id": safe_int(row.get("user_id")),
                    "url": safe_str(row.get("url")),
                    "referrer": safe_str(row.get("referrer")),
                    "device_type": safe_str(row.get("device_type")) or "desktop",
                    "user_agent": safe_str(row.get("user_agent")),
                    "ip": safe_str(row.get("ip")),
                    "payload": safe_payload(row.get("payload_json")),
                })

            r = client.post(API_URL, json=events)
            r.raise_for_status()

if __name__ == "__main__":
    main()