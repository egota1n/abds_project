-- DAU, количество сессий и событий
CREATE TABLE IF NOT EXISTS mart.active_users_daily
(
  date Date,
  dau UInt64,
  sessions UInt64,
  events UInt64
)
ENGINE = ReplacingMergeTree
ORDER BY date;

-- CTR страниц (views vs clicks)
CREATE TABLE IF NOT EXISTS mart.page_ctr_daily
(
  date Date,
  url String,
  views UInt64,
  clicks UInt64,
  ctr Float64
)
ENGINE = ReplacingMergeTree
ORDER BY (date, url);

-- Средняя длительность пользовательских сессий
CREATE TABLE IF NOT EXISTS mart.session_duration_daily
(
  date Date,
  avg_session_duration_sec Float64
)
ENGINE = ReplacingMergeTree
ORDER BY date;

-- Распределение устройств
CREATE TABLE IF NOT EXISTS mart.device_share_daily
(
  date Date,
  device_type String,
  events UInt64,
  users UInt64
)
ENGINE = ReplacingMergeTree
ORDER BY (date, device_type);

-- Funnel событий по элементам интерфейса
CREATE TABLE IF NOT EXISTS mart.element_funnel_daily
(
  date Date,
  event_title String,
  element_id String,
  views UInt64,
  clicks UInt64,
  click_to_view Float64
)
ENGINE = ReplacingMergeTree
ORDER BY (date, event_title, element_id);