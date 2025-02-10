# Module 3: Data Warehousing

## OLAP vs OLTP
### OLTP
Stands for ONline Transaction Processing
- Used on the backend side of things, grouping SQL queries together in order to roll- or fallback in case of error
- Short, user initiated data updates in small chunks
- Normalized for efficiency
- Comparatively small
- Backups are essential to ensure functionality of business
- Focused on end-users

### OLAP
Stands for ONline Analytics Processing
- Used to store heaps of data for analytical purpose, to discover hidden insights
- Extensive, long running data updates, usually done periodically and in batches
- Denormalized for easier analysis
- Comparatively large
- Instead of backups, typically is re-ingested from a OLTP database on loss 
- Focused on business managers, analysts and executives

## What is a data warehouse?
Data warehouses are OLAP solutions, that ingest data from various sources, such as:
- Opreational Systems
- OLTP Databases
- Flat files (i.e. from a bucket)

And proceed to transform an manage them as
- Raw Data
- Meta Data
- Summary Data

This data can then be used to form data marts, providing insight to different business units, such as puchasing, sales or inventory management. These in turn can be accessed by various business people.

## BigQuery
- Serverless data warehouse
- IaaS and SaaS helps with high scalability and availability, as well as lower costs
- Provides inbuilt features for machine learning, geopacial analytics or business intelligence

### For this course
- BigQuery caches results for increased efficiency. This may lead to unexpected results, so for this traning, we turn it off (More > Resource Management > Cache preference)
- There are _many_ openly available data warehouses hosted in BigQuery which can just be searched and/or included


### Creating an external table
BigQuery supports flat files for inclusion in the data lake. To do so, we can create an external table using SQL:
```
CREATE OR REPLACE EXTERNAL TABLE `zoomcamp.external_yellow_tripdata`
OPTIONS(
  format = 'PARQUET',
  uris = [
    "gs://my_bucket_name/yellow_tripdata_2024-01.parquet",
    "gs://my_bucket_name/yellow_tripdata_2024-02.parquet",
    "gs://my_bucket_name/yellow_tripdata_2024-03.parquet",
    "gs://my_bucket_name/yellow_tripdata_2024-04.parquet",
    "gs://my_bucket_name/yellow_tripdata_2024-05.parquet",
    "gs://my_bucket_name/yellow_tripdata_2024-06.parquet"
  ]
);
```
In this example, we ingest the ny taxi trip data for the first half of 2024, stored in `my_bucket_name` - a google cloud storage bucket. This will be created as a table in the zoomcamp dataset. Notice, how the details section does not contain any storage size information, since no space is taken in BigQuery but rather only the storage bucket.

It is important to notice, that BigQuery won't allow for accessing data between regions. Therefor, the dataset must reside in the same region as your bucket.

## Partitioning
Partitions will sort data into sections based on a specific criteria, for example a date.
Partitions can help impove query speed and cost, since less data needs to be searched to find a specific set of information.

Creating a partitioned table is simple:
```
CREATE OR REPLACE TABLE `zoomcamp.yellow_tripdata_partitioned`
PARTITION BY
  DATE(tpep_pickup_datetime) AS 
SELECT * FROM `zoomcamp-bigquery.zoomcamp.external_yellow_tripdata`
```

Once the data is partitioned, we can gather some insight into the partitions by runngin the following query:
```
SELECT * FROM zoomcamp.INFORMATION_SCHEMA.PARTITIONS
WHERE table_name = 'yellow_tripdata_partitioned'
ORDER BY total_rows DESC
```

## Clusters
To further improve performance, data can be clustered. This means, that information within a specific partition will be sorted ad groupd based on a secondary criteria. As an example: one could partition taxi trips by the date they occured, and cluster by vendor ID. The critera for clustering should be based on your use case. Select the proerty which is queried most often.

Clusters may be created using SQL as follows:
```
CREATE OR REPLACE TABLE `zoomcamp.yellow_tripdata_partitioned_and_clustered`
PARTITION BY
  DATE(tpep_pickup_datetime) 
CLUSTER BY
  VendorID AS
SELECT * FROM `zoomcamp-bigquery.zoomcamp.external_yellow_tripdata`
```

## Homework
### Question 5
In order to provide best efficiency for the specified queries, we partition by `tpep_dropoff_datetime`, so we can focus our queries on the interesting timeframe. We then cluster by VendorID, to pre-organize our records.
```
CREATE OR REPLACE TABLE `zoomcamp.yellow_tripdata_dropoff`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID AS
SELECT * FROM `zoomcamp-bigquery.zoomcamp.external_yellow_tripdata`
```
