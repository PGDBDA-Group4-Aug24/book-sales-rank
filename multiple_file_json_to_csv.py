import boto3
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_unixtime, date_format, input_file_name, regexp_extract

# Initialize Spark session
spark = SparkSession.builder.appName("JSONToCSV_MultipleFiles").getOrCreate()

# Define input and output S3 paths
input_folder = "s3://group4-buck/ranks_norm/ranks_norm/ranks_norm/"
output_file = "s3://group4-buck/output_csv/"

# List objects using pagination
file_paths = []
continuation_token = None
while True:
    list_params = {"Bucket": bucket_name, "Prefix": prefix}
    if continuation_token:
        list_params["ContinuationToken"] = continuation_token

    response = s3_client.list_objects_v2(**list_params)
    file_paths.extend(content['Key'] for content in response.get('Contents', []))
    continuation_token = response.get('NextContinuationToken')
    if not continuation_token:
        break

# Limit the files to process
files_to_process = file_paths[:10000]

# Read the JSON files
df = spark.read.option("multiLine", "true").json(
    [f"s3://{bucket_name}/{file}" for file in files_to_process]
)


# Extract ASIN dynamically from the file name using input_file_name()
df = df.withColumn("file_name", input_file_name())  # Get full file path
df = df.withColumn("asin", regexp_extract(col("file_name"), r".*/([^/]+)_com_norm.json", 1))  # Extract ASIN

# Extract timestamp columns dynamically (excluding "asin" and "file_name")
timestamp_cols = [c for c in df.columns if c not in ["asin", "file_name"]]

# Convert wide format to long format (melt)
# Use stack() with backticks around the column names for the value part
df_long = df.selectExpr("asin", f"stack({len(timestamp_cols)}, " + 
                        ", ".join([f"'{c}', `{c}`" for c in timestamp_cols]) + ") as (timestamp, rank)")

# Convert timestamp to proper date/time format
df_long = df_long.withColumn("timestamp", from_unixtime(col("timestamp").cast("long"))) \
                 .withColumn("year", date_format(col("timestamp"), "yyyy")) \
                 .withColumn("month", date_format(col("timestamp"), "MM")) \
                 .withColumn("date", date_format(col("timestamp"), "dd")) \
                 .withColumn("day", date_format(col("timestamp"), "EEEE")) \
                 .withColumn("hour", date_format(col("timestamp"), "HH"))

# Select final columns
df_final = df_long.select("timestamp", "rank", "asin", "year", "month", "date", "day", "hour")

# Write to CSV
try:
    df_final.coalesce(1).write.mode("overwrite").option("header", "true").csv(output_file)
except Exception as e:
    print(f"Error writing CSV: {str(e)}")

print(f"Total records: {df_final.count()}")

# Stop the Spark session
spark.stop()