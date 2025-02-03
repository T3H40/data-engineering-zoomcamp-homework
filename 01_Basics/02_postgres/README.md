# Module 1

## Using the ingestion Dockerfile

Create a docker container `docker build -t postgres-ingest:0.0.1 .`.  
This creates a container with the given ingestion script. Now we can run it:

```
docker run -v=/Users/tsiebeneichler/Downloads/zoomcamp/data:/data --network=pg-network postgres-ingest:0.0.1 --host=db --table=nyc_green_tripdata --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz --db=ny_taxi

docker run -v=/Users/tsiebeneichler/Downloads/zoomcamp/data:/data --network=pg-network postgres-ingest:0.0.1 --host=db --table=taxi_zone_lookup --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv --db=ny_taxi
Downloading from URL: https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```