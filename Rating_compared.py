pip install pandas

from pyspark.sql import SparkSession

# Create Spark session
spark = SparkSession.builder.appName("JoinCSV").getOrCreate()

# Load CSV files from DBFS (Databricks File System)
df1 = spark.read.csv("dbfs:/FileStore/Amazon_project/books_info_ratings.csv", header=True, inferSchema=True)
df2 = spark.read.csv("dbfs:/FileStore/Amazon_project/updated_dataset_with_genretest2.csv", header=True, inferSchema=True)

df1.printSchema()
df2.printSchema()
from pyspark.sql.functions import lower
from pyspark.sql.functions import col

result = df1.withColumn("Book Title", lower(col("Book Title"))) \
    .join(df2.withColumn("TITLE", lower(col("TITLE"))), col("Book Title") == col("TITLE"), "inner")

from pyspark.sql.functions import trim

result = df1.withColumn("Book Title", trim(col("Book Title"))) \
    .join(df2.withColumn("TITLE", trim(col("TITLE"))), col("Book Title") == col("TITLE"), "inner")

result.write.csv("dbfs:/mnt/data/output.csv", header=True, mode="overwrite")

count_result = result.count()
print(f"Total count after join: {count_result}")
display(result)

filtered_df = result.filter((col("Rating") != "NA") & (col("Rating").isNotNull()))

# Show filtered results
filtered_df.show()
display(filtered_df)
unique_titles_df = filtered_df.dropDuplicates(["Book Title"])

# Show the result
unique_titles_df.show(truncate=False)
display(unique_titles_df)
