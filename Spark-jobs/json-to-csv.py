from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, from_unixtime, date_format, input_file_name, regexp_extract

# Initialize Spark session
spark = SparkSession.builder.appName("JSONToCSV_MultipleFiles").getOrCreate()

# Define input and output S3 paths
input_folder = "s3a://amabook/book_json_file/"  # Folder containing multiple JSON files
output_file = "s3a://amabook/output_bookcsv/"  # Output CSV location

# Read all JSON files from the input folder
df = spark.read.option("multiLine", "true").json(input_folder + "*.json")

# Extract ASIN dynamically from the file name using `input_file_name()`
df = df.withColumn("file_name", input_file_name())  # Get full file path
df = df.withColumn("asin", regexp_extract(col("file_name"), r".*/([^/]+)_com_norm.json", 1))  # Extract ASIN

# Extract timestamp columns dynamically (excluding "asin" and "file_name")
timestamp_cols = [c for c in df.columns if c not in ["asin", "file_name"]]

# Convert wide format to long format (melt)
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

# Write the DataFrame to a single CSV file
df_final.coalesce(1).write.mode("overwrite").option("header", "true").csv(output_file)

# Stop the Spark session
spark.stop()