books_df = spark.read.option('header', True).csv("dbfs:/FileStore/Amazon_project/updated_dataset_with_genretest2.csv",
                                                 encoding='ISO-8859-1')
books_df.printSchema()
print(books_df.head())
books_df1 = books_df.toDF('ASIN', 'GROUP', 'FORMAT', 'TITLE', 'AUTHOR', 'PUBLISHER', 'Genre')
books_df1.show(5)
# from pyspark.sql.functions import udf
# from pyspark.sql.types import StructType, StructField, StringType
# import requests

# # Function to get Google Books details based on the title
# def get_google_books_details_by_title(title):
#     url = f"https://www.googleapis.com/books/v1/volumes"
#     params = {
#         'q': f'intitle:{title}'  # Search for books with the given title
#     }
#     response = requests.get(url, params=params)

#     if response.status_code == 200:
#         data = response.json()
#         if "items" in data:
#             # Extract relevant details like title, author, reviews, and ratings
#             book_info = data["items"][0]["volumeInfo"]
#             title = book_info.get("title", "No Title")
#             authors = ", ".join(book_info.get("authors", ["No Author"]))  # Join authors into a string
#             ratings = book_info.get("averageRating", "No Rating")
#             return (title, authors, ratings)
#         else:
#             return (title, "No Author", "No Rating")
#     else:
#         return (title, "No Author", "No Rating")

# # UDF to apply to each row of the DataFrame (now returns a tuple that Spark can process)
# def fetch_book_details(title):
#     book_details = get_google_books_details_by_title(title)
#     return book_details

# # Register the UDF to be used in Spark DataFrame with a STRUCT type
# book_details_schema = StructType([
#     StructField("title", StringType(), True),
#     StructField("authors", StringType(), True),
#     StructField("ratings", StringType(), True)
# ])

# fetch_book_details_udf = udf(fetch_book_details, book_details_schema)

# # Assuming books_df1 is your DataFrame and has a 'TITLE' column
# # Apply the UDF to the DataFrame and create new columns for the results
# book_details_df = books_df1.withColumn("book_details", fetch_book_details_udf(books_df1['TITLE']))

# # Now, we can extract the individual columns from the book_details column (which is now a struct)
# book_details_df = book_details_df.select(
#     "TITLE",
#     "book_details.title",
#     "book_details.authors",
#     "book_details.ratings"
# )

# # Show the result
# book_details_df.show()
# from pyspark.sql.functions import col

# # Filter rows where ratings is "No Rating"
# filtered_books_df = book_details_df.filter(col("book_details.ratings") != "No Rating")

# # Show the filtered DataFrame
# filtered_books_df.show()


# from pyspark.sql.functions import col

# # Filter rows where ratings is not None (or replace None with 'No Rating' if needed)
# filtered_books_df = book_details_df.filter(col("book_details.ratings").isNotNull())

# # Show the filtered DataFrame
# filtered_books_df.show()
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StructType, StructField, StringType
import requests


# Function to get Google Books details based on the title
def get_google_books_details_by_title(title):
    url = f"https://www.googleapis.com/books/v1/volumes"
    params = {'q': f'intitle:{title}'}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        if "items" in data:
            book_info = data["items"][0]["volumeInfo"]
            title = book_info.get("title", "No Title")
            authors = ", ".join(book_info.get("authors", ["No Author"]))  # Join authors into a string
            ratings = book_info.get("averageRating", None)  # Use None if no rating
            return (title, authors, ratings)
        else:
            return (title, "No Author", None)  # Return None for ratings if no book is found
    else:
        return (title, "No Author", None)  # Handle error case and return None for ratings


# UDF to apply to each row of the DataFrame (now returns a tuple that Spark can process)
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

# Assuming books_df1 is your DataFrame and has a 'TITLE' column
# Apply the UDF to the DataFrame and create new columns for the results
book_details_df = books_df1.withColumn("book_details", fetch_book_details_udf(books_df1['TITLE']))

# Now, we can extract the individual columns from the book_details column (which is now a struct)
book_details_df = book_details_df.select(
    "TITLE",
    "book_details.title",
    "book_details.authors",
    "book_details.ratings"
)

# Filter rows where ratings is None (skip rows with no ratings)
filtered_books_df = book_details_df.filter(col("book_details.ratings").isNotNull())

# Show the filtered DataFrame
filtered_books_df.show()

# from pyspark.sql.functions import col

# # Filter rows where ratings is not null and is a valid numeric value (5, 4.5, 3, etc.)
# filtered_books_df = book_details_df.filter(
#     col("book_details.ratings").isNotNull() & (col("book_details.ratings") != "No Rating")
# )

# # Show the filtered DataFrame (only rows with valid ratings)
# filtered_books_df.show()
# from pyspark.sql.functions import col

# # Filter out rows where ratings is null
# filtered_books_df = book_details_df.filter(col("book_details.ratings").isNotNull())

# # Show the filtered DataFrame
# filtered_books_df.show()

from pyspark.sql.functions import col

# Access the 'ratings' field inside the 'book_details' struct
filtered_books_df = book_details_df.filter(col("book_details.ratings").isNotNull())

# Show the filtered DataFrame
filtered_books_df.show()

# Drop rows where the 'ratings' field inside the 'book_details' struct is null
filtered_books_df = book_details_df.dropna(subset=["ratings"])

# Show the filtered DataFrame
filtered_books_df.show()

filtered_books_df.display()
filtered_books_df.write \
    .option("header", "true") \
    .csv("dbfs:/FileStore/Amazon_project")
book_details_df.printSchema()
# Drop rows where the 'ratings' field inside the 'book_details' struct is null
# book_details_df = book_details_df.na.drop(subset=["ratings"])
book_details_df = book_details_df.dropna(subset=["ratings"])

# Show the filtered DataFrame
filtered_books_df.show()
# Drop the original TITLE column if it's redundant
book_details_df_dropped = book_details_df.drop("TITLE")

# Write the DataFrame to CSV
book_details_df_dropped.write \
    .option("header", "true") \
    .csv("dbfs:/FileStore/Amazon_project/book")



