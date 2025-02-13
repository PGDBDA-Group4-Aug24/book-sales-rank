import requests
import pandas as pd
import os
import time

# File paths
input_csv = "updated_dataset_with_genretest2.csv"  # Your input CSV file
output_csv = "BOOK.csv"  # Output file with page numbers

# Function to fetch page count from Google Books API
def fetch_page_number_from_google_books(title):
    try:
        search_url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title.replace(' ', '%20')}"
        response = requests.get(search_url)

        if response.status_code != 200:
            print(f"Failed to retrieve data for '{title}'. Status: {response.status_code}")
            return "Not available"

        data = response.json()

        # Debugging: Print API response for first book
        if "items" in data and len(data["items"]) > 0:
            book = data["items"][0]
            if "volumeInfo" in book and "pageCount" in book["volumeInfo"]:
                return book["volumeInfo"]["pageCount"]
            else:
                return "Page count not available"
        else:
            return "Book not found"

    except Exception as e:
        print(f"Error fetching page number for {title}: {e}")
        return "Error"

# Function to update CSV file with page numbers
def fetch_page_numbers_from_csv(input_csv, output_csv):
    # Load existing data if output file exists
    if os.path.exists(output_csv):
        df = pd.read_csv(output_csv, encoding="ISO-8859-1")
    else:
        df = pd.read_csv(input_csv, encoding="ISO-8859-1")

    # Ensure 'PageNumber' column exists
    if "PageNumber" not in df.columns:
        df["PageNumber"] = ""

    # Ensure column name matches CSV
    if "TITLE" not in df.columns:
        print("Error: 'TITLE' column not found in the CSV. Available columns:", df.columns)
        return

    # Process each book
    for index, row in df.iterrows():
        title = row["TITLE"]

        # Skip if page number is already fetched
        if pd.notna(row["PageNumber"]) and row["PageNumber"] != "":
            continue

        print(f"\nFetching page number for: {title}")
        page_number = fetch_page_number_from_google_books(title)

        # Update dataframe
        df.at[index, "PageNumber"] = page_number

        # Save after every book to prevent data loss
        df.to_csv(output_csv, index=False, encoding="ISO-8859-1")
        print(f"Updated {title} with {page_number} pages.")

        # To avoid hitting API rate limits
        time.sleep(2)

    print(f"\nProcess completed. Results saved in {output_csv}")

# Run the function
fetch_page_numbers_from_csv(input_csv, output_csv)
