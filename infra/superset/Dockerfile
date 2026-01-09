FROM apache/superset:3.0.0

USER root

RUN pip uninstall -y clickhouse-sqlalchemy sqlalchemy-clickhouse || true
RUN pip install --no-cache-dir clickhouse-connect

USER superset