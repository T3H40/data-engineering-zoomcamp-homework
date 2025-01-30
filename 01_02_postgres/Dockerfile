FROM python:3.9.1

RUN pip install pandas requests sqlalchemy psycopg2-binary

WORKDIR /app
COPY data_ingestion.py data_ingestion.py

ENTRYPOINT ["python", "data_ingestion.py"]