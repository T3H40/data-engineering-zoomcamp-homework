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

Now, load the data into the database. To do so, you can run `data_ingestion.py`, somewhat like this:
```
python data-engineering-zoomcamp-homework/01/02_postgres/data_ingestion.py \
    --user=root \
    --password=root \
    --host=localhost \
    --port=5432 \
    --db=ny_taxi \
    --table=nyc_green_tripdata \
    --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz
```

### Docker
The provided Dockerfile can be used to create a container image for data ingestion. It will run the python script mentioned above and try to insert thee content into the configured database.

Helpful commands:
```bash
docker ps                         # list running containers
docker kill abc123                # kills running container
docker build -t someimage:1.2.3 . # builds image from Dockerfile
docker run -it someimage:1.2.3    # starts a new container running someimage interactively
```

You can go ahead and orchestrate multiple containers by creating a docer-compose file.
The `services:` section will hold all containers to spool up.  
All containers you define will automatically be placed within a network.

Use `docker compose up` to run your composition in your current directory, or, you can pass a path to a docker-compose file elsewhere usinf `-f`. The `-d` flag will run in detached mode.

Use `docker compose down`to gracefully shutdown.

### Handy tips
- Run `python -m http.server` to run a simple http server on the fly from your current directory

### Terraform
Infrastructure as code. Helps setting up (and tearing down!) systems for use.

You can define providers for differnet clouds to access.  

Important commands are:
```bash
terraform init    # Get the selected cloud provider
terraform plan    # Shows the steps that are going to be followed / ressoures created
terraform apply   # perform actions defined in .tf file
terraform destroy # remove what is defined in .tf file
```

First, we need to create means of authentication for terraform. For GCP this boils down to:
- Go to IAM & Admin > Service Accounts
- Create new Service Account
  - Name: "terraform runner"
  - Access Roles (Add as needed but limit as much as possible):
    - Cloud Storage > Storage Admin (for creating a bucket)
    - BigQuery > Big Query Admin (for creating a BigQuery dataset)
    - Compute Engine > Compute Admin (for creating instances)
- Create access Key to use the new service account:
  - Go to Service Accounts > Our Service Account > ... > Manage Keys
  - Add Key > Create new Key (JSON)
  - The private(!!!) key file will be downloaded

This json credential file can be used in the project from here on out.

Next, we setup a project. For the project we
- Create subfolder "keys" and store our certificate
- Create a `main.tf` file for terraform
- You can copy the base usage code from the, e.g.: https://registry.terraform.io/providers/hashicorp/google/latest/docs
- You can find the project id by going to Cloud Overview > Dashboard in the Google Cloud burger menu 

The `main.tf` file contains your connection setup, cou cann now run
```bash
terraform init
```
to initialize the connection and run the commands
```bash
terraform plan
terraform apply
```
to see wether the desired changes would be done and to actually apply them if happy.
This will create a `terraform.tfstate` file, containing various bits of state info on your infrastructure.

Once done, you can run `terraform destroy` to remove all created resources again.

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
SELECT
    CASE
        WHEN trip_distance <= 1 THEN 'Up to 1 mile'
        WHEN trip_distance > 1 AND trip_distance <= 3 THEN '1~3 miles'
        WHEN trip_distance > 3 AND trip_distance <= 7 THEN '3~7 miles'
        WHEN trip_distance > 7 AND trip_distance <= 10 THEN '7~10 miles'
        ELSE '10+ miles'
    END AS segment,
    to_char(COUNT(1), '999,999') AS num_trips
FROM
    nyc_green_tripdata
WHERE
    lpep_pickup_datetime >= '2019-10-01'
    AND lpep_pickup_datetime < '2019-11-01'
    AND lpep_dropoff_datetime >= '2019-10-01'
    AND lpep_dropoff_datetime < '2019-11-01'
GROUP BY
    segment
```
We get the following counts:
```
"10+ miles"     | "  35,189"
"1~3 miles"	    | " 198,924"
"3~7 miles"	    | " 109,603"
"7~10 miles"    | "  27,678"
"Up to 1 mile"	| " 104,802"
```
Explanation: We analyse every line in the table, we then create an output column called `segment`, that we fill with a value based on the trip_distance of each row using `CASE`.

The second column of our output is called `num_trips` which we format using `to_char()`. The content of that column will be `COUNT(1)` since we count the number of rows. The `1` acts as filler to give `COUNT` something to count. We could have used any column name instead without a noticable difference.

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
ORDER BY t DESC
```

Which outputs:
```
"East Harlem North"   |	1236 | 18686.680000000084
"East Harlem South"	  | 1101 | 16797.26000000006
"Morningside Heights" |	764  | 13029.790000000025
```
Notice, that we order by the sum of `total_amount`, as we define the "largest" region as most generated revenue.

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
