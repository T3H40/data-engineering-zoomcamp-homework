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

## Best practices
When working with data warehouses, there are some best practices to keep in mind to get the best efficiency in terms of

cost:
- Avoid `SELECT *`queries. Since BigQuery stores in columnar format, selecting unneeded columns leads to additional memory reads
- Price queries before running them (Refactor for best variant)
- Use clustered and partitioned tables in order to improve speed and reduce memory access
- Use streaming inserts with caution, since they can increase cost. Prefer batched inserts instead.
- Materialize results in stages, to not have to redo them

and speed:
- Filter on partitioned column, to make use of paritionoing
- Denormalize data to trade storage cost for speed
- Use nested and repeated columns
- Use external data sources sparingly. Reading from storage might be more expensive than materializing
- Don't treat `WITH`clauses as prepared statements.
- Avoid oversharding. Data can be split into shards to simplify restoration after a failure. Bigger shards take longer to restore, but smaller shards slow down query execution. Aim for 10-50GB per shard as a benchmark.
- Avoid JavaScript
- Use approximate aggregation functions
- `ORDER`should be the last statement
- Reduce data before using a JOIN, also when joining declate the largest table first and the smalest table secod to minimize reads

## Internals of BigQuery
### Colossus
Cheap storage where BigQuery stores the data in columar format. This spearation from storage and compute is very cost efficient.

### Jupiter
Jupiter is the network(ing technology) used to connect the components of BigQuery within the datacenters, with query speeds up to 1TB/s.

### Dremel
This is the query execution engine. It organizes the Query in a tree structure and separates execution of different threads.

## Machine Learning in BigQuery
ML in BigQuery is targeted at Data analysts and managers, not requiring knowledge in Python or Java, as well as exporting data from the warehouse to a different system. Instead, the model can be build in the warehouse directly.

To create a new model, we need to define a value to predict and intake information.
In this example, we want to predict the tip_amount based on general ride information. Trips with total cost 0 are excluded.

```sql
SELECT 
  passenger_count, trip_distance, PULocationID, DOLocationID, payment_type, fare_amount, tolls_amount, tip_amount
FROM 
  `taxi-rides-ny.nytaxi.yellow_tripdata_partitioned` 
WHERE 
  fare_amount != 0;
```

Next, we define a schema for our processing data. We adapt some of the values to make them more digestable for machine learning. In detail, we replace the column type of our categorial integer columns (like `payment_type`) into strings, since different values here do not corellate to a specific order but rather just represent different types of value (e.g. card or cash payment).

```sql
CREATE OR REPLACE TABLE `taxi-rides-ny.nytaxi.yellow_tripdata_ml` (
    `passenger_count` INTEGER,
    `trip_distance` FLOAT64,
    `PULocationID` STRING,
    `DOLocationID` STRING,
    `payment_type` STRING,
    `fare_amount` FLOAT64,
    `tolls_amount` FLOAT64,
    `tip_amount` FLOAT64
) AS (
    SELECT passenger_count, trip_distance, cast(PULocationID AS STRING), CAST(DOLocationID AS STRING),
    CAST(payment_type AS STRING), fare_amount, tolls_amount, tip_amount
FROM `taxi-rides-ny.nytaxi.yellow_tripdata_partitioned` WHERE fare_amount != 0
);
```

With this information now available to us, we define a model that we want to use for our prediction:

```sql
CREATE OR REPLACE MODEL `taxi-rides-ny.nytaxi.tip_model`
OPTIONS
    (model_type='linear_reg',
    input_label_cols=['tip_amount'],
    DATA_SPLIT_METHOD='AUTO_SPLIT') AS
SELECT
    *
FROM
    `taxi-rides-ny.nytaxi.yellow_tripdata_ml`
WHERE
    tip_amount IS NOT NULL;
```

This creates a new model for us. Data was automatically split into learning and evaluation data.
We can further investigate the features of our model:

```sql
SELECT * FROM ML.FEATURE_INFO(MODEL `taxi-rides-ny.nytaxi.tip_model`);
```

This shows us different aspects of our data. Notice, that columns like `payment_type` don't have numerical attributes like min/max.

We can test our model by checking it against existing data using `ML.EVALUATE`

```sql
SELECT
  *
FROM
  ML.EVALUATE(MODEL `taxi-rides-ny.nytaxi.tip_model`,
    (
    SELECT
    *
    FROM
    `taxi-rides-ny.nytaxi.yellow_tripdata_ml`
    WHERE
    tip_amount IS NOT NULL
));
```

or by actually creating predictions:

```sql
SELECT
  *
FROM
    ML.PREDICT(MODEL `taxi-rides-ny.nytaxi.tip_model`,
    (
    SELECT
    *
    FROM
    `taxi-rides-ny.nytaxi.yellow_tripdata_ml`
    WHERE
    tip_amount IS NOT NULL
    ));
```

Aside from predicting, we can also have BigQuery explain the top most important parameters used during the prediction:
```sql
SELECT
    *
    FROM
    ML.EXPLAIN_PREDICT(MODEL `taxi-rides-ny.nytaxi.tip_model`,
    (
    SELECT
    *
    FROM
    `taxi-rides-ny.nytaxi.yellow_tripdata_ml`
    WHERE
    tip_amount IS NOT NULL
    ), STRUCT(3 as top_k_features));
```

To follow up our test, we could now perform some hyper marameter tuning in order to improve the result.
The following query shows some of them:

```sql
CREATE OR REPLACE MODEL `taxi-rides-ny.nytaxi.tip_hyperparam_model`
    OPTIONS
    (model_type='linear_reg',
    input_label_cols=['tip_amount'],
    DATA_SPLIT_METHOD='AUTO_SPLIT',
    num_trials=5,
    max_parallel_trials=2,
    l1_reg=hparam_range(0, 20),
    l2_reg=hparam_candidates([0, 0.1, 1, 10])) AS
    SELECT
    *
    FROM
    `taxi-rides-ny.nytaxi.yellow_tripdata_ml`
    WHERE
    tip_amount IS NOT NULL;
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
