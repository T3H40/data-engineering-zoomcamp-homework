#!/usr/bin/env python
# coding: utf-8

import argparse
import gzip
import shutil
import tempfile

import pandas as pd
import requests
from sqlalchemy import create_engine

def download_csv(url):
    print(f"Downloading from URL: {url}")
    response = requests.get(url, allow_redirects=True, stream=True)
    response.raise_for_status()  # Ensure we notice bad responses

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    print(f"Created temporary file: {temp_file.name}")

    if url.endswith('.gz'):
        print("Detected .gz file, decompressing...")
        with open(temp_file.name, 'wb') as f_out:
            with gzip.GzipFile(fileobj=response.raw) as f_in:
                shutil.copyfileobj(f_in, f_out)
            response.raw.decode_content = True
    else:
        print("Downloading regular CSV file...")
        with open(temp_file.name, 'wb') as f:
            f.write(response.content)

    print("Download completed successfully")
    return temp_file.name

def ingest_data(user, password, host, port, db, table, filename):
    # Create DB engine
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    # Create iterator for table data and insert first row into DB:
    it = pd.read_csv(filename, chunksize=100000)
    chunk = next(it)

    if 'lpep_pickup_datetime' in chunk.columns and 'lpep_dropoff_datetime' in chunk.columns:
        chunk.lpep_pickup_datetime = pd.to_datetime(chunk.lpep_pickup_datetime)
        chunk.lpep_dropoff_datetime = pd.to_datetime(chunk.lpep_dropoff_datetime)

    chunk.head(n=0).to_sql(table, con=engine, if_exists='replace')
    chunk.to_sql(table, con=engine, if_exists='append')
    chunk = next(it, None)

    while chunk is not None:
        if 'lpep_pickup_datetime' in chunk.columns and 'lpep_dropoff_datetime' in chunk.columns:
            chunk.lpep_pickup_datetime = pd.to_datetime(chunk.lpep_pickup_datetime)
            chunk.lpep_dropoff_datetime = pd.to_datetime(chunk.lpep_dropoff_datetime)
        chunk.to_sql(table, con=engine, if_exists='append')
        cnt = len(chunk)
        print(f'Chunk {cnt} loaded')
        chunk = next(it, None)

def main():
    parser = argparse.ArgumentParser(description='Ingest CSV data into postgres')
    parser.add_argument('--user', default='root', help='username')
    parser.add_argument('--password', default='root', help='password')
    parser.add_argument('--host', default='localhost', help='host')
    parser.add_argument('--port', default=5432, help='port')
    parser.add_argument('--db', help='database name')
    parser.add_argument('--table', required=True, help='table name')
    parser.add_argument('--url', required=True, help='intake URL for CSV data')

    args = parser.parse_args()

    filename = download_csv(args.url)
    ingest_data(args.user, args.password, args.host, args.port, args.db, args.table, filename)

if __name__ == '__main__':
    main()

"""
python data-engineering-zoomcamp-homework/01_02_postgres/data_ingestion.py \
    --user=root \
    --password=root \
    --host=localhost \
    --port=5432 \
    --db=ny_taxi \
    --table=nyc_green_tripdata \
    --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz

python data-engineering-zoomcamp-homework/01_02_postgres/data_ingestion.py \
    --user=root \
    --password=root \
    --host=localhost \
    --port=5432 \
    --db=ny_taxi \
    --table=taxi_zone_lookup \
    --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
"""
