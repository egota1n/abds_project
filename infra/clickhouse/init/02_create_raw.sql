-- Сырые clickstream-события без трансформаций
CREATE TABLE IF NOT EXISTS raw.events
(
  -- Уникальный идентификатор события
  id UUID DEFAULT generateUUIDv4(),

  -- Тип события: view | click
  type LowCardinality(String),

  -- Время генерации события на клиенте
  created_at DateTime64(3, 'UTC'),

  -- Время приёма события системой
  received_at DateTime64(3, 'UTC'),

  -- Идентификатор пользовательской сессии
  session_id String,

  -- Идентификатор пользователя
  user_id UInt64,

  -- IPv4-адрес клиента
  ip String,

  -- URL страницы
  url String,

  -- URL источника перехода
  referrer String,

  -- Тип устройства: desktop | mobile | tablet
  device_type LowCardinality(String),

  -- User-Agent клиента
  user_agent String,

  -- Сырой payload события в формате JSON
  payload String,

  -- Источник данных: http | rabbitmq | csv
  source LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY toDate(created_at)
ORDER BY (toDate(created_at), session_id, created_at)
SETTINGS index_granularity = 8192;