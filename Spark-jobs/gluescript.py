import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['group4'])
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['group4'], args)

from pyspark.sql.functions import (
    input_file_name, from_json, explode, col, split, lit, from_unixtime,
    date_format, concat_ws, to_timestamp, min as spark_min
)
from pyspark.sql.types import MapType, StringType, LongType

input_path = "s3://rank-norm-data/*.json"  # Update with your S3 path
df_text = spark.read.text(input_path).withColumn("file_name", input_file_name())

#Parse JSON Content
json_schema = MapType(StringType(), LongType())
df_map = df_text.withColumn("json_map", from_json(col("value"), json_schema))
df_exploded = df_map.select("file_name", explode(col("json_map")).alias("timestamp", "rank"))
# # Initialize boto3 client for S3
# s3_client = boto3.client('s3')
#
# # Extract the bucket and prefix from the input path
# bucket_name = input_folder.split('/')[2]
# prefix = '/'.join(input_folder.split('/')[3:])
#
# # List objects using pagination
# file_paths = []
# continuation_token = None
# while True:
#     list_params = {"Bucket": bucket_name, "Prefix": prefix}
#     if continuation_token:
#         list_params["ContinuationToken"] = continuation_token
#
#     response = s3_client.list_objects_v2(**list_params)
#     file_paths.extend(content['Key'] for content in response.get('Contents', []))
#     continuation_token = response.get('NextContinuationToken')
#     if not continuation_token:
#         break
#
# # Limit the files to process
# files_to_process = file_paths[:10000]
#
# # Read the JSON files
# df = spark.read.option("multiLine", "true").json(
#     [f"s3://{bucket_name}/{file}" for file in files_to_process]
# )


# Extract ASIN dynamically from the file name using `input_file_name()`
# df = df.withColumn("file_name", input_file_name())  # Get full file path
# df = df.withColumn("asin", regexp_extract(col("file_name"), r".*/([^/]+)_com_norm.json", 1))  # Extract ASIN

# Extract ASIN from the File Name
df_exploded = df_exploded.withColumn("base_filename", split(col("file_name"), "/").getItem(3))
df_exploded = df_exploded.withColumn("asin", split(col("base_filename"), "_").getItem(0))


# Extract timestamp columns dynamically (excluding "asin" and "file_name")
# timestamp_cols = [c for c in df.columns if c not in ["asin", "file_name"]]
#
# # Convert wide format to long format (melt)
# df_long = df.selectExpr("asin", f"stack({len(timestamp_cols)}, " +
#                         ", ".join([f"'{c}', `{c}`" for c in timestamp_cols]) + ") as (timestamp, rank)")

# Convert timestamp to proper date/time format
df_exploded = df_exploded.withColumn("timestamp", from_unixtime(col("timestamp").cast("long"))) \
                 .withColumn("year", date_format(col("timestamp"), "yyyy")) \
                 .withColumn("month", date_format(col("timestamp"), "MM")) \
                 .withColumn("date", date_format(col("timestamp"), "dd")) \
                 .withColumn("day", date_format(col("timestamp"), "EEEE")) \
                 .withColumn("hour", date_format(col("timestamp"), "HH"))

# Select final columns
final_df = df_exploded.select("asin", "timestamp", "rank", "year", "month", "date", "day", "hour")

# Load the CSV File with Metadata and Merge via Inner Join on asin

csv_file_path = "s3://mergedjsontoparquet/books_with_8_genres.csv"  # Update with your actual CSV path
metadata_df = spark.read.option("header", "true").csv(csv_file_path)
final_df = final_df.join(metadata_df, on="asin", how="inner")

# Group Daily Data and Aggregate
final_df = final_df.dropna()

# Group by daily values and additional metadata columns.
df_daily = final_df.groupBy(
    "asin", "year", "month", "date", "day", "GROUP", "FORMAT", "TITLE", "AUTHOR", "PUBLISHER", "GENRE"
).agg(
    spark_min("rank").alias("rank")  # choose the minimum rank for that day
)

# Select the desired columns (adjust order as needed)
df_daily = df_daily.select(
    "asin", "timestamp", "rank", "year", "month", "date", "day",
    "GROUP", "FORMAT", "TITLE", "AUTHOR", "PUBLISHER", "GENRE"
)

# Write the Final Merged DataFrame (Daily Aggregated) to S3 as Parquet
output_path = "s3://merged-df/gluejob/"  # Update with your S3 output path
df_daily.write.mode("overwrite").parquet(output_path)
print("Processed files, grouped daily, and merged into a single output.")

#df_daily.coalesce(1).write.mode("overwrite").option("header", "true").csv("s3://merged-df/all-csv/")

job.commit()
#spark.stop()
