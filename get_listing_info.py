import json
import re
from datetime import datetime

import requests

# link = "https://www.facebook.com/marketplace/item/611908928559542/"
link = "https://www.facebook.com/marketplace/item/1363526394799665"

listing_id = re.search(r"/item/(\d+)/?", link).group(1)

headers = {"sec-fetch-site": "same-origin"}
data = {
    "variables": json.dumps({"targetId": listing_id}),
    "doc_id": "24259665626956870",
}
response = requests.post(
    "https://www.facebook.com/api/graphql/",
    headers=headers,
    data=data,
)

data = response.json()
creation_time = data["data"]["viewer"]["marketplace_product_details_page"]["target"]["creation_time"]  # unix timestamp
creation_time = datetime.fromtimestamp(creation_time)
lat = data["data"]["viewer"]["marketplace_product_details_page"]["target"]["location"]["latitude"]
lng = data["data"]["viewer"]["marketplace_product_details_page"]["target"]["location"]["longitude"]
name = data["data"]["viewer"]["marketplace_product_details_page"]["target"]["marketplace_listing_title"]
print(creation_time, lat, lng, name)
