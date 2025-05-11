import json
import re
from datetime import datetime

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

link = "https://www.facebook.com/marketplace/item/2225569484525431"

# First get cookies using Selenium
options = Options()
options.add_argument("--headless")  # Run in headless mode
driver = webdriver.Chrome(options=options)

# Visit the marketplace page to get cookies
driver.get("https://www.facebook.com/marketplace")
cookies = driver.get_cookies()
driver.quit()

# Convert Selenium cookies to requests format
cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies}

listing_id = re.search(r"/item/(\d+)/?", link).group(1)

headers = {"sec-fetch-site": "same-origin"}
data = {
    "variables": json.dumps({"targetId": listing_id}),
    "doc_id": "9668679113214200",
}

response = requests.post(
    "https://www.facebook.com/api/graphql/",
    headers=headers,
    data=data,
    cookies=cookies_dict,
)

data = response.json()
creation_time = data["data"]["viewer"]["marketplace_product_details_page"]["target"]["creation_time"]  # unix timestamp
creation_time = datetime.fromtimestamp(creation_time)
lat = data["data"]["viewer"]["marketplace_product_details_page"]["target"]["location"]["latitude"]
lng = data["data"]["viewer"]["marketplace_product_details_page"]["target"]["location"]["longitude"]
location = data["data"]["viewer"]["marketplace_product_details_page"]["target"]["location_text"]["text"]
name = data["data"]["viewer"]["marketplace_product_details_page"]["target"]["marketplace_listing_title"]
price = data["data"]["viewer"]["marketplace_product_details_page"]["target"]["formatted_price"]["text"]
print(creation_time, lat, lng, location, name, price)
