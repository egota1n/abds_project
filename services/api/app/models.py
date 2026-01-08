from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

# Типы событий
EventType = Literal["view", "click"]
# Типы устройств
DeviceType = Literal["desktop", "mobile", "tablet"]

class EventPayload(BaseModel):
    # Бизнес-тип события (checkout, promo_click и т.д.)
    event_title: str = Field(..., min_length=1, max_length=64)

    # CSS-идентификатор элемента интерфейса
    element_id: Optional[str] = Field(default="", max_length=256)

    # Координата клика по оси X
    x: Optional[int] = Field(default=0, ge=0, le=100_000)

    # Координата клика по оси Y
    y: Optional[int] = Field(default=0, ge=0, le=100_000)


class ClickstreamEvent(BaseModel):
    # Тип события
    type: EventType

    # Время генерации события
    created_at: datetime

    # Идентификатор пользовательской сессии
    session_id: str = Field(..., min_length=1, max_length=128)

    # Идентификатор пользователя
    user_id: int = Field(..., ge=1)

    # URL страницы
    url: str = Field(..., min_length=1, max_length=2048)

    # URL источника перехода
    referrer: str = Field(default="", max_length=2048)

    # Тип устройства
    device_type: DeviceType = "desktop"

    # User-Agent клиента
    user_agent: str = Field(default="", max_length=512)

    # IPv4-адрес клиента
    ip: str = Field(default="", max_length=64)

    # Payload события
    payload: EventPayload


class IngestResponse(BaseModel):
    # Количество вставленных событий
    inserted: int