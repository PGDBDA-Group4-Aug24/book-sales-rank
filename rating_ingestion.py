from pyspark.sql.functions import udf, col
from pyspark.sql.types import StructType, StructField, StringType
import requests

# Load the books dataframe using PySpark
books_df = spark.read.option("header", True).csv('dbfs:/FileStore/Final_Project/amazon_com_extras.csv')

# Print books dataframe schema
books_df.printSchema()

# List of columns to drop
columns_to_drop = ['_c6', '_c7', '_c8', '_c9', '_c10', '_c11', '_c12', '_c13', '_c14']

# Drop the unwanted columns
books_df_cleaned = books_df.drop(*columns_to_drop)

# Show the cleaned dataframe
books_df_cleaned.show(truncate=False)

# Rename columns for clarity
books_df1 = books_df_cleaned.toDF("ASIN", "GROUP", "FORMAT", "TITLE", "AUTHOR", "PUBLISHER")
books_df1.show()

# Function to get Google Books details based on the title
def get_google_books_details_by_title(title):
    url = f"https://www.googleapis.com/books/v1/volumes"
    params = {'q': f'intitle:{title}'}  # Search for books with the given title
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "items" in data:
            # Extract relevant details like title, author, reviews, and ratings
            book_info = data["items"][0]["volumeInfo"]
            title = book_info.get("title", "No Title")
            authors = ", ".join(book_info.get("authors", ["No Author"]))  # Join authors into a string
            ratings = book_info.get("averageRating", "No Rating")
            return (title, authors, ratings)
        else:
            return (title, "No Author", "No Rating")
    else:
        return (title, "No Author", "No Rating")

# UDF to fetch book details using the above function
def fetch_book_details(title):
    book_details = get_google_books_details_by_title(title)
    return book_details

# Register the UDF to be used in Spark DataFrame with a STRUCT type
book_details_schema = StructType([
    StructField("title", StringType(), True),
    StructField("authors", StringType(), True),
    StructField("ratings", StringType(), True)
])

fetch_book_details_udf = udf(fetch_book_details, book_details_schema)

# Apply the UDF to fetch book details for each title
book_details_df = books_df1.withColumn("book_details", fetch_book_details_udf(books_df1['TITLE']))

# Select the required fields from the STRUCT column 'book_details'
book_details_df = book_details_df.select(
    "TITLE",                                     
    "book_details.title", 
    "book_details.authors", 
    "book_details.ratings"
)

# Show the resulting DataFrame
book_details_df.show(truncate=False)

# Filter rows where ratings are not "No Rating"
rated_books_df = book_details_df.filter((col("ratings").isNotNull()) & (col("ratings") != "No Rating"))

# Show the filtered DataFrame
rated_books_df.show(truncate=False)

# Register the DataFrame as a temporary SQL view
book_details_df.createOrReplaceTempView("books_details")

# SQL query to filter out rows where ratings are not "No Rating"
query = """
SELECT * 
FROM books_details 
WHERE ratings != 'No Rating'
"""

# Execute the SQL query
rated_books_df_sql = spark.sql(query)

# Show the result of the SQL query
rated_books_df_sql.show(truncate=False)

# Optionally display the final DataFrame in Databricks
display(book_details_df)
