import boto3
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_unixtime, date_format, input_file_name, from_json, explode, lit , date_format
from pyspark.sql.types import MapType, StringType, LongType

# Initialize Spark session
spark = SparkSession.builder.appName("ProcessJSONFilesDirectly").getOrCreate()

# Define input and output S3 paths
# The wildcard pattern will instruct Spark to read all JSON files in the directory.
input_path = "s3://rank-norm-data/*.json"
output_file = "s3://group4-buck/output_csv/"

df_text = spark.read.text(input_path).withColumn("file_name", input_file_name())

# List objects using pagination
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


# # Extract ASIN dynamically from the file name using input_file_name()
# df = df.withColumn("file_name", input_file_name())  # Get full file path
# df = df.withColumn("asin", regexp_extract(col("file_name"), r".*/([^/]+)_com_norm.json", 1))  # Extract ASIN

# Extract timestamp columns dynamically (excluding "asin" and "file_name")
# timestamp_cols = [c for c in df.columns if c not in ["asin", "file_name"]]
#
# # Convert wide format to long format (melt)
# # Use stack() with backticks around the column names for the value part
# df_long = df.selectExpr("asin", f"stack({len(timestamp_cols)}, " +
#                         ", ".join([f"'{c}', `{c}`" for c in timestamp_cols]) + ") as (timestamp, rank)")

# Define a schema for the JSON: each file is a JSON object (map) with string keys (timestamps) and long values (ranks)
json_schema = MapType(StringType(), LongType())
df_map = df_text.withColumn("json_map", from_json(col("value"), json_schema))

# Explode the map so each key-value pair becomes a separate row with columns "timestamp" and "rank"
df_exploded = df_map.select("file_name", explode(col("json_map")).alias("timestamp", "rank"))

# First, extract the base filename from the full S3 path.
# For example, if file_name is "s3://rank-norm-data/0007204493_com_norm.json",
# splitting on "/" and taking the last element returns "0007204493_com_norm.json".
df_exploded = df_exploded.withColumn("base_filename", split(col("file_name"), "/").getItem(3))
# Next, split the base filename on "_" and take the first part to get the ASIN.
df_exploded = df_exploded.withColumn("asin", split(col("base_filename"), "_").getItem(0))

# Convert timestamp to proper date/time format
df_exploded = df_exploded.withColumn("timestamp", from_unixtime(col("timestamp").cast("long"))) \
                 .withColumn("year", date_format(col("timestamp"), "yyyy")) \
                 .withColumn("month", date_format(col("timestamp"), "MM")) \
                 .withColumn("date", date_format(col("timestamp"), "dd")) \
                 .withColumn("day", date_format(col("timestamp"), "EEEE")) \
                 .withColumn("hour", date_format(col("timestamp"), "HH"))

# Select final columns
df_final = df_exploded.select("timestamp", "rank", "asin", "year", "month", "date", "day", "hour")

# Write to CSV
try:
    output_path = "s3://alljsontoparquet/output/"
    final_df.write.mode("overwrite").parquet(output_path)
    print("Processed files and merged into a single output.")
except Exception as e:
    print(f"Error writing CSV: {str(e)}")

print(f"Total records: {df_final.count()}")

# Stop the Spark session
spark.stop()