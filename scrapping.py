import requests
from bs4 import BeautifulSoup
import csv
import time


def get_publisher(asin):
    url = f"https://www.amazon.com/dp/{asin}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        print(f"Error fetching ASIN {asin}: {e}")
        return None

    if response.status_code != 200:
        print(f"Error: status code {response.status_code} for ASIN {asin}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    publisher = None

    # Check detail bullets section (newer Amazon layout)
    detail_div = soup.find("div", id="detailBullets_feature_div")
    if detail_div:
        lis = detail_div.find_all("li")
        for li in lis:
            text = li.get_text(separator=" ", strip=True)
            if "Publisher:" in text:
                publisher = text.split("Publisher:")[-1].split("(")[0].strip()
                break

    # If not found, try the product details table (alternative layouts)
    if not publisher:
        for table_id in ["productDetails_detailBullets_sections1", "productDetails_techSpec_section_1"]:
            table = soup.find("table", id=table_id)
            if table:
                rows = table.find_all("tr")
                for row in rows:
                    header = row.find("th")
                    if header and "Publisher" in header.get_text():
                        td = row.find("td")
                        if td:
                            publisher = td.get_text(strip=True)
                            break
            if publisher:
                break

    return publisher


def main():
    input_file = "Book3.csv"  # CSV file with columns: ASIN, TITLE, AUTHOR
    output_file = "books_with_publisher.csv"

    with open(input_file, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    for row in rows:
        asin = row["ASIN"].strip()
        print(f"Processing ASIN: {asin}")
        pub = get_publisher(asin)
        row["PUBLISHER"] = pub if pub else "Not Found"
        time.sleep(2)  # Avoid hitting Amazon too frequently

    fieldnames = ["ASIN", "TITLE", "AUTHOR", "PUBLISHER"]
    with open(output_file, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Output written to {output_file}")


if __name__ == "__main__":
    main()
