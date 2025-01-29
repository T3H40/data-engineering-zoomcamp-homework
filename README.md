# Data Engineering Zoomcamp 2025

This repo contains notes and homework for the DataTalks Data Engineering Zoomcamp 2025

Homework can be submitted to: https://courses.datatalks.club/de-zoomcamp-2025/
Data can be found here: https://github.com/DataTalksClub/nyc-tlc-data

## Module 1 - Setup
Test that the docker engine setup works:
```bash
docker run hello-world
docker run -it ubuntu bash
```
`-it` enables interactive input.

To extend existing images, create a Dockerfile, e.g.:
```
FROM python:3.12.8

RUN pip install pandas

ENTRYPOINT ["bash"]
```
Then build and run the image.
```
docker build -t test:pandas 01_pandas_image
[...output...]

docker run -it test:pandas
root@76029731e354:/# python
Python 3.12.8 (main, Jan 24 2025, 19:38:26) [GCC 12.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import pandas
>>> pandas.__version__
'2.2.3'
```

Next up, run a local postgres instance in a docker container:
```bash
docker run -it \
    -e POSTGRES_USER=root \
    -e POSTGRES_PASSWORD=root \
    -e POSTGRES_DB=ny_taxi \
    -v G:/Data-Engineering-Zoomcamp/data \
    -p 5432:5432 \
    postgres:13
```

Also, install pgcli module:
```bash
py -m pip install pgcli
```

Make sure, you have a current Python version installed!  
In my case, I needed to install rust and some dependency:
```
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup target add i686-pc-windows-msvc
py -m pip install pgcli sqlalchemy psycopg2
py -m pgcli --help
```
Now connect to local DB:
```
py -m pgcli -h localhost -p 5432 -u root -d ny_taxi
Password for root:root
Server: PostgreSQL 13.18 (Debian 13.18-1.pgdg120+1)
Version: 4.1.0
Home: http://pgcli.com
root@localhost:ny_taxi>

```
Success :) 

Now, load the data into the databae. See the data_ingestion.ipynb notebook.


### Homework Q1
Run Dockers Python container, start off with bash,
then check pip version:
```
$ docker run -it python:3.12.8 bash
root@8b0515083b93:/# pip --version
pip 24.3.1 from /usr/local/lib/python3.12/site-packages/pip (python 3.12)
```

### Homework Q2
Port 5433 is for accessing the internal container network from the host machine, whereas 5432 is the internal port.
The machine is listed as `db` in the compose file, together with `postgres` as a container name. Either is valid to address the container.

Therefor, both `postgres:5432` and `db:5432` are valid answers.

### Homework Q3
To collect all trips matching the requirements, we use the following query:
```
SELECT COUNT(*) FROM nyc_green_tripdata WHERE Trip_distance <= 1
SELECT COUNT(*) FROM nyc_green_tripdata WHERE Trip_distance > 1 AND Trip_distance <= 3
SELECT COUNT(*) FROM nyc_green_tripdata WHERE Trip_distance > 3 AND Trip_distance <= 7
SELECT COUNT(*) FROM nyc_green_tripdata WHERE Trip_distance > 7 AND Trip_distance <= 10
SELECT COUNT(*) FROM nyc_green_tripdata WHERE Trip_distance < 10
```
We get the following counts:
`104838,199013,109645,27688,35202` 

### Homework Q4
To find the longest trip we run the following query:
```
SELECT lpep_pickup_datetime, MAX(Trip_distance) as mx 
FROM nyc_green_tripdata 
GROUP BY lpep_pickup_datetime 
ORDER BY mx DESC 
LIMIT 1
```
Which returns `2019-10-31` 

### Homework Q5
To find the requested Areas, we run the following query:
```
SELECT 
  "Zone", COUNT(*) AS cnt, SUM(total_amount) AS "t" 
FROM 
  nyc_green_tripdata AS td 
JOIN 
  taxi_zone_lookup AS tz ON td."PULocationID" = tz."LocationID" 
WHERE 
  lpep_pickup_datetime >= '2019-10-18'::date AND lpep_pickup_datetime < '2019-10-19'::date 
GROUP BY "Zone" 
ORDER BY cnt DESC
```

Which outputs:
```
| Zone                                | cnt  | total              |
|-------------------------------------+------+--------------------|
| East Harlem North                   | 1236 | 18686.680000000084 |
| East Harlem South                   | 1101 | 16797.260000000053 |
```

### Homework Q6

To find the longest trip, we run:
```
SELECT 
  tz2."Zone", MAX(Tip_amount) AS mx 
FROM 
  nyc_green_tripdata AS td 
JOIN 
  taxi_zone_lookup AS tz ON td."PULocationID" = tz."LocationID" 
JOIN 
  taxi_zone_lookup AS tz2 ON td."DOLocationID" = tz2."LocationID" 
WHERE 
  tz."Zone" = 'East Harlem North'
GROUP 
  BY tz2."Zone" ORDER BY mx DESC
```
Which returns
```
+-------------------------------------+-------+
| Zone                                | mx    |
|-------------------------------------+-------|
| JFK Airport                         | 87.3  |
```
