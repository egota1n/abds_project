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


def _fmt(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _fmt_date(d):
    return d.strftime("%Y-%m-%d")

"""
Очистка и нормализация raw событий:
    - фильтрация по типу события
    - парсинг payload
    - загрузка в dwh.events_clean
"""
def load_dwh(**context):
    start = _fmt(context["data_interval_start"])
    end = _fmt(context["data_interval_end"])

    sql = f"""
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
        coalesce(JSONExtractString(payload, 'element_id'), '') AS element_id,
        toUInt32(ifNull(JSONExtractInt(payload, 'x'), 0)) AS x,
        toUInt32(ifNull(JSONExtractInt(payload, 'y'), 0)) AS y,
        source
    FROM raw.events
    WHERE
        type IN ('view', 'click')
        AND user_id > 0
        AND id IS NOT NULL
        AND created_at >= toDateTime('{start}')
        AND created_at < toDateTime('{end}')
    """
    run_clickhouse_sql(sql)


"""
Построение аналитических витрин:
    - активные пользователи
    - Heatmap/Line chart кликов элементов к их просмотрам
    - CTR страниц
    - cредняя длительность сессии пользователя
    - распределение устройств
    - топ траниц
"""
def build_marts(**context):
    day = _fmt_date(context["data_interval_start"].date())

    deletes = [
        f"ALTER TABLE mart.active_users_daily DELETE WHERE date = toDate('{day}')",
        f"ALTER TABLE mart.page_ctr_daily DELETE WHERE date = toDate('{day}')",
        f"ALTER TABLE mart.device_share_daily DELETE WHERE date = toDate('{day}')",
        f"ALTER TABLE mart.element_funnel_daily DELETE WHERE date = toDate('{day}')",
        f"ALTER TABLE mart.session_duration_daily DELETE WHERE date = toDate('{day}')",
    ]

    for sql in deletes:
        run_clickhouse_sql(sql)

    inserts = [

        # DAU / sessions / events
        f"""
        INSERT INTO mart.active_users_daily
        SELECT
            toDate(created_at) AS date,
            uniqExact(user_id) AS dau,
            uniqExact(session_id) AS sessions,
            count() AS events
        FROM dwh.events_clean
        WHERE toDate(created_at) = toDate('{day}')
        GROUP BY date
        """,

        # CTR по страницам
        f"""
        INSERT INTO mart.page_ctr_daily
        SELECT
            toDate(created_at) AS date,
            url,
            countIf(type = 'view') AS views,
            countIf(type = 'click') AS clicks,
            if(views = 0, 0.0, clicks / toFloat64(views)) AS ctr
        FROM dwh.events_clean
        WHERE toDate(created_at) = toDate('{day}')
        GROUP BY date, url
        """,

        # Доли устройств
        f"""
        INSERT INTO mart.device_share_daily
        SELECT
            toDate(created_at) AS date,
            device_type,
            count() AS events,
            uniqExact(user_id) AS users
        FROM dwh.events_clean
        WHERE toDate(created_at) = toDate('{day}')
        GROUP BY date, device_type
        """,

        # Funnel / Heatmap элементов
        f"""
        INSERT INTO mart.element_funnel_daily
        SELECT
            toDate(created_at) AS date,
            event_title,
            element_id,
            countIf(type = 'view') AS views,
            countIf(type = 'click') AS clicks,
            if(views = 0, 0.0, clicks / toFloat64(views)) AS click_to_view
        FROM dwh.events_clean
        WHERE
            element_id != ''
            AND toDate(created_at) = toDate('{day}')
        GROUP BY date, event_title, element_id
        """,

        # Длительность сессии
        f"""
        INSERT INTO mart.session_duration_daily
        SELECT
            date,
            avg(session_duration_sec) AS avg_session_duration_sec
        FROM
        (
            SELECT
                toDate(min(created_at)) AS date,
                session_id,
                dateDiff(
                    'second',
                    min(created_at),
                    max(created_at)
                ) AS session_duration_sec
            FROM dwh.events_clean
            WHERE
                session_id != ''
                AND toDate(created_at) = toDate('{day}')
            GROUP BY session_id
        )
        GROUP BY date
        """
    ]

    for sql in inserts:
        run_clickhouse_sql(sql)


with DAG(
    dag_id="clickstream_etl",
    start_date=datetime(2025, 1, 1),
    schedule_interval="*/5 * * * *",
    catchup=False,
    is_paused_upon_creation=False,
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