from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
import clickhouse_connect


# ClickHouse connection настройки
CLICKHOUSE_HOST = "clickhouse"
CLICKHOUSE_PORT = 8123


# Выполнение SQL-запроса в ClickHouse
def run_clickhouse_sql(sql: str):
    client = clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT
    )
    client.command(sql)

"""
Очистка и нормализация raw событий:
    - фильтрация по типу события
    - парсинг payload
    - загрузка в dwh.events_clean
"""
def load_dwh():
    sql = """
    INSERT INTO dwh.events_clean
    SELECT
        id,
        type,
        created_at,
        received_at,
        session_id,
        user_id,
        ip,
        url,
        coalesce(referrer, '') AS referrer,
        device_type,
        user_agent,
        JSONExtractString(payload, 'event_title') AS event_title,
        JSONExtractString(payload, 'element_id') AS element_id,
        toUInt32(JSONExtractInt(payload, 'x')) AS x,
        toUInt32(JSONExtractInt(payload, 'y')) AS y,
        source
    FROM raw.events
    WHERE
        type IN ('view', 'click')
        AND user_id > 0
        AND created_at IS NOT NULL
    """
    run_clickhouse_sql(sql)


"""
Построение аналитических витрин:
    - активные пользователи
    - CTR страниц
    - распределение устройств
"""
def build_marts():
    sqls = [
        # DAU / sessions / events
        """
        INSERT INTO mart.active_users_daily
        SELECT
            toDate(created_at) AS date,
            uniqExact(user_id) AS dau,
            uniqExact(session_id) AS sessions,
            count() AS events
        FROM dwh.events_clean
        GROUP BY date
        """,
        
        # CTR по страницам
        """
        INSERT INTO mart.page_ctr_daily
        SELECT
            toDate(created_at) AS date,
            url,
            countIf(type = 'view') AS views,
            countIf(type = 'click') AS clicks,
            if(views = 0, 0, clicks / views) AS ctr
        FROM dwh.events_clean
        GROUP BY date, url
        """,
        
        # Доли устройств
        """
        INSERT INTO mart.device_share_daily
        SELECT
            toDate(created_at) AS date,
            device_type,
            count() AS events,
            uniqExact(user_id) AS users
        FROM dwh.events_clean
        GROUP BY date, device_type
        """
    ]

    for sql in sqls:
        run_clickhouse_sql(sql)


with DAG(
    dag_id="clickstream_etl",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["clickstream", "etl"],
) as dag:

    # Загрузка и очистка raw -> dwh
    load_dwh_task = PythonOperator(
        task_id="load_dwh_events",
        python_callable=load_dwh,
    )

    # Построение аналитических витрин
    build_marts_task = PythonOperator(
        task_id="build_marts",
        python_callable=build_marts,
    )

    load_dwh_task >> build_marts_task