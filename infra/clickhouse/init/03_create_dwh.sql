-- Очищенные и нормализованные clickstream-события
CREATE TABLE IF NOT EXISTS dwh.events_clean
(
  -- Идентификатор события
  id UUID,

  -- Тип события
  type LowCardinality(String),

  -- Время генерации события
  created_at DateTime64(3, 'UTC'),

  -- Время приёма события
  received_at DateTime64(3, 'UTC'),

  -- Идентификатор сессии
  session_id String,

  -- Идентификатор пользователя
  user_id UInt64,

  -- IPv4-адрес клиента
  ip String,

  -- URL страницы
  url String,

  -- URL источника перехода
  referrer String,

  -- Тип устройства
  device_type LowCardinality(String),

  -- User-Agent клиента
  user_agent String,

  -- Бизнес-тип события
  event_title LowCardinality(String),

  -- Идентификатор DOM-элемента
  element_id String,

  -- Координата клика по оси X
  x UInt32,

  -- Координата клика по оси Y
  y UInt32,

  -- Источник данных
  source LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY toDate(created_at)
ORDER BY (toDate(created_at), session_id, created_at);