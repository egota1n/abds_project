from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Iterable, Dict, Any
import httpx

def ch_datetime(dt: str) -> str:
    return (
        dt.replace("T", " ")
        .replace("Z", "")
        .split(".")[0]
    )

class ClickHouseClient:
    def __init__(self, base_url: str, database: str = "raw", table: str = "events") -> None:
        self.base_url = base_url.rstrip("/")
        self.database = database
        self.table = table
    
    async def insert_raw_events(self, events, source: str) -> int:
        rows = []
        now = datetime.now(timezone.utc).isoformat(timespec="milliseconds")

        for e in events:
            rows.append({
                "type": e["type"],
                "created_at": ch_datetime(e["created_at"]),
                "received_at": ch_datetime(now),
                "session_id": e["session_id"],
                "user_id": int(e["user_id"]),
                "ip": e.get("ip", ""),
                "url": e["url"],
                "referrer": e.get("referrer", ""),
                "device_type": e.get("device_type", "desktop"),
                "user_agent": e.get("user_agent", ""),
                "payload": json.dumps(e.get("payload", {}), ensure_ascii=False),
                "source": source,
            })

        data = "\n".join(
            json.dumps(r, ensure_ascii=False) for r in rows
        ) + "\n"

        query = f"INSERT INTO {self.table} FORMAT JSONEachRow"

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self.base_url}/",
                params={
                    "database": self.database,
                    "user": "default",
                    "query": query,
                },
                content=data.encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()

        return len(rows)