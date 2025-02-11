from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Initialize Spark session
spark = SparkSession.builder.appName('MergingCleaning').getOrCreate()

# Read the CSV file from S3
df1 = spark.read.csv('s3://project-buck-chinmay/10000_csv/part-00000-d0a0df4d-1abd-4101-bae3-a5d9e2088f33-c000.csv', header=True, inferSchema=True)
df1.show(10)

# Define window specification
window_spec = Window.partitionBy('asin').orderBy('timestamp')

# Use 'last' function to fill forward 'rank' values within each 'asin' partition
df_filled = df1.withColumn('rank', F.last('rank', ignorenulls=True).over(window_spec))
df_filled.show(20)

# Count nulls in each column
null_counts = df_filled.select([F.count(F.when(F.col(c).isNull(), c)).alias(c) for c in df_filled.columns])
null_counts.show()

# Total counts of each column
total_counts = df_filled.select([F.count(F.col(c)).alias(c) for c in df_filled.columns])
total_counts.show()

# Drop rows where any column has null values
df_cleaned = df_filled.dropna()
df_cleaned.show()

# Read another dataset containing genres
genre_df = spark.read.csv('s3://project-buck-chinmay/10000_csv/updated_dataset_with_genretest2.csv', header=True, inferSchema=True)
genre_df.show(50)

# Merge the dataframes on 'asin' column
merged_df = genre_df.join(df_cleaned, on='asin', how='inner')
merged_df.show(50)

# Show distinct 'rank' values
unique_ranks = df_filled.select('rank').distinct()
unique_ranks.show()
print("Total unique ranks:", unique_ranks.count())

# Stop the Spark session
spark.stop()
