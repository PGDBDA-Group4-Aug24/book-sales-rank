import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# ********************
# Glue Job Initialization
# ********************
args = getResolvedOptions(sys.argv, ['group4'])
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['group4'], args)

# ********************
# STEP 1: Read All JSON Files from S3 Using Wildcard
# ********************
from pyspark.sql.functions import (
    input_file_name, from_json, explode, col, split, lit, from_unixtime, 
    date_format, concat_ws, to_timestamp, min as spark_min
)
from pyspark.sql.types import MapType, StringType, LongType

input_path = "s3://rank-norm-data/*.json"  # Update with your S3 path
df_text = spark.read.text(input_path).withColumn("file_name", input_file_name())

# ********************
# STEP 2: Parse JSON Content
# ********************
json_schema = MapType(StringType(), LongType())
df_map = df_text.withColumn("json_map", from_json(col("value"), json_schema))
df_exploded = df_map.select("file_name", explode(col("json_map")).alias("timestamp", "rank"))

# ********************
# STEP 3: Extract ASIN from the File Name
# ********************
df_exploded = df_exploded.withColumn("base_filename", split(col("file_name"), "/").getItem(3))
df_exploded = df_exploded.withColumn("asin", split(col("base_filename"), "_").getItem(0))

# ********************
# STEP 4: Convert Timestamps and Extract Date Parts
# ********************
df_exploded = df_exploded.withColumn("timestamp", from_unixtime(col("timestamp").cast("long"))) \
                         .withColumn("year", date_format(col("timestamp"), "yyyy")) \
                         .withColumn("month", date_format(col("timestamp"), "MM")) \
                         .withColumn("date", date_format(col("timestamp"), "dd")) \
                         .withColumn("day", date_format(col("timestamp"), "EEEE")) \
                         .withColumn("hour", date_format(col("timestamp"), "HH"))

# ********************
# STEP 5: Select the Final Columns from the Exploded DataFrame
# ********************
final_df = df_exploded.select("asin", "timestamp", "rank", "year", "month", "date", "day", "hour")

# ********************
# STEP 6: Load the CSV File with Metadata and Merge via Inner Join on asin
# ********************
csv_file_path = "s3://mergedjsontoparquet/books_with_8_genres.csv"  # Update with your actual CSV path
metadata_df = spark.read.option("header", "true").csv(csv_file_path)
final_df = final_df.join(metadata_df, on="asin", how="inner")

# ********************
# NEW STEP: Group Daily Data and Aggregate
# ********************
final_df = final_df.dropna()

# Group by daily values and additional metadata columns.
df_daily = final_df.groupBy(
    "asin", "year", "month", "date", "day", "GROUP", "FORMAT", "TITLE", "AUTHOR", "PUBLISHER", "GENRE"
).agg(
    spark_min("rank").alias("rank")  # choose the minimum rank for that day
)

# Create a timestamp column from year, month, and date
df_daily = df_daily.withColumn(
    "timestamp",
    to_timestamp(concat_ws("-", col("year"), col("month"), col("date")), "yyyy-MM-dd")
)


# Select the desired columns (adjust order as needed)
df_daily = df_daily.select(
    "asin", "timestamp", "rank", "year", "month", "date", "day",
    "GROUP", "FORMAT", "TITLE", "AUTHOR", "PUBLISHER", "GENRE"
)

# ********************
# STEP 7: Write the Final Merged DataFrame (Daily Aggregated) to S3 as Parquet
# ********************
output_path = "s3://merged-df/gluejob/"  # Update with your S3 output path
df_daily.write.mode("overwrite").parquet(output_path)
print("Processed files, grouped daily, and merged into a single output.")

job.commit()
