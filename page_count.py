# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# import re  # Regular expression module for parsing text
#
# # Setup Selenium WebDriver
# options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Run in the background
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#
# # Open Amazon Book Page
# driver.get(
#     "https://www.amazon.in/Shine-Benedict-Stone-Phaedra-Patrick/dp/0778330893/ref=sr_1_1?crid=XK8JWR49LNML&dib=eyJ2IjoiMSJ9.SOYNKRoDTPglsce_lrujbA.mYTCIgfSWxO36ERUmNGgAYnIn7MOXFES9VDe09yEkOo&dib_tag=se&keywords=Rise+and+Shine%2C+Benedict+Stone%3A+A+Novel&qid=1738134656&sprefix=rise+and+shine%2C+benedict+stone+a+novel%2Caps%2C2142&sr=8-1")  # Replace with a real book URL
#
# # Extract book title
# title = driver.find_element(By.ID, "productTitle").text
#
# # Initialize the details dictionary
# book_details = {
#     "Title": title,
#     "Length (Pages)": None,
#     "Language": None,
#     "Publication Date": None,
#     "Dimensions": None
# }
#
# # Try to extract the details from the product information section
# try:
#     # Locate the product details section
#     details_section = driver.find_element(By.ID, "productDetails_detailBullets_sections1")
#
#     # Loop through each <li> element in the product details section
#     for li in details_section.find_elements(By.TAG_NAME, "li"):
#         text = li.text.strip()
#
#         # Check for "pages"
#         if "page" in text.lower():
#             book_details["Length (Pages)"] = text
#
#         # Check for "Language"
#         elif "language" in text.lower():
#             book_details["Language"] = text.split(":")[1].strip() if ":" in text else text
#
#         # Check for "Publication date"
#         elif "publication date" in text.lower():
#             book_details["Publication Date"] = text.split(":")[1].strip() if ":" in text else text
#
#         # Check for "Dimensions"
#         elif "dimension" in text.lower():
#             book_details["Dimensions"] = text
#
#     # Print the details
#     print(f"Book Title: {book_details['Title']}")
#     print(f"Length (Pages): {book_details['Length (Pages)']}")
#     print(f"Language: {book_details['Language']}")
#     print(f"Publication Date: {book_details['Publication Date']}")
#     print(f"Dimensions: {book_details['Dimensions']}")
#
# except Exception as e:
#     print(f"Error extracting details: {e}")
#
# # Close the driver
# driver.quit()
