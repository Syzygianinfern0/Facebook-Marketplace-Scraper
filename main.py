import json
import logging
import random
import re
import time
from datetime import datetime, timedelta

import apprise
import requests
import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from sheets import Sheets


def random_sleep():
    time.sleep(random.randint(1, 3))


def get_listing_info(link, cookies=None):
    listing_id = re.search(r"/item/(\d+)/?", link).group(1)

    headers = {"sec-fetch-site": "same-origin"}
    if cookies:
        # Convert Selenium cookies to name:value dict
        cookies = {cookie["name"]: cookie["value"] for cookie in cookies}

    data = {
        "variables": json.dumps({"targetId": listing_id}),
        "doc_id": "24259665626956870",
    }
    response = requests.post(
        "https://www.facebook.com/api/graphql/",
        headers=headers,
        data=data,
        cookies=cookies,
    )

    data = response.json()
    target = data["data"]["viewer"]["marketplace_product_details_page"]["target"]

    return {
        "creation_time": datetime.fromtimestamp(target["creation_time"]),
        "location": target["location_text"]["text"],
        "latitude": target["location"]["latitude"],
        "longitude": target["location"]["longitude"],
        "title": target["marketplace_listing_title"],
    }


def parse_price(price_str):
    if price_str.lower() == "free":
        return 0
    # Extract all numeric characters
    numeric_str = re.sub(r"[^\d]", "", price_str)
    if not numeric_str:
        return float("inf")  # Return infinity for non-numeric prices
    return int(numeric_str)


class FacebookMarketplaceScraper:
    def __init__(self, headless=True):
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if headless:
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)

    def click_close_button(self):
        close_button = self.driver.find_element(By.XPATH, "//div[@aria-label='Close']")
        close_button.click()

    def get_listings(self, query):
        # Open the website
        with open("config.yaml", "r") as f:
            configs = yaml.safe_load(f)
        location = configs.get("location", "austin")  # Default to austin if not specified
        self.driver.get(f"https://www.facebook.com/marketplace/{location}/search/?query={query}")
        self.click_close_button()

        # Scroll down
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(3)

        # Get all the links
        links = self.driver.find_elements(By.TAG_NAME, "a")
        cleaned_links = []
        for link in links:
            href = link.get_attribute("href")
            if href and href.startswith("https://www.facebook.com/marketplace/item/"):
                cleaned_links.append(href.split("?")[0])
        logging.info(f"Found {len(cleaned_links)} links for {query} on marketplace")

        # get prices from css selector ".xjkvuk6.xkhd6sd .x1s688f"
        prices = self.driver.find_elements(By.CSS_SELECTOR, ".xjkvuk6.xkhd6sd .x1s688f")
        prices = [price.text for price in prices]
        # print(prices)
        assert len(prices) == len(cleaned_links)
        prices = {link: price for link, price in zip(cleaned_links, prices)}

        return cleaned_links, prices

    def close(self):
        self.driver.quit()


def main():
    scraper = FacebookMarketplaceScraper(headless=True)

    # Set up the notification service
    apobj = apprise.Apprise()
    with open("config.yaml", "r") as f:
        configs = yaml.safe_load(f)
    apobj.add(configs["apprise"])

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Get the queries
    sheets = Sheets()
    queries = sheets.get_queries()

    # Get the links
    links = {}
    prices = {}
    for query in queries.keys():
        links[query], prices[query] = scraper.get_listings(query)
        random_sleep()

    # Check if the links are new
    for query, new_links in links.items():
        old_links = sheets.get_links(query)
        new_links = [link for link in new_links if link not in old_links]

        # Get detailed info for new links
        listing_info = {}
        total_links = len(new_links)

        logging.info(f"Processing {total_links} new links for query: {query}")

        for i, link in enumerate(new_links, 1):
            try:
                listing_info[link] = get_listing_info(link, cookies=scraper.driver.get_cookies())
                if i % 5 == 0 or i == total_links:  # Log every 5 links and at the end
                    logging.info(f"Processed {i}/{total_links} links for {query}")
                random_sleep()  # Add delay between API calls
            except Exception as e:
                logging.error(f"Error getting listing info for {link}: {str(e)}")
                # Try one more time after a delay
                try:
                    time.sleep(5)  # Wait 5 seconds before retry
                    logging.info(f"Retrying to get info for {link}")
                    listing_info[link] = get_listing_info(link, cookies=scraper.driver.get_cookies())
                except Exception as e:
                    logging.error(f"Failed again to get listing info for {link}: {str(e)}")
                    apobj.notify(body=f"Failed to get listing info for {link}: {str(e)}")
                    continue

        # Update sheets with all new links and their info
        sheets.update_links(query, new_links, prices[query], listing_info)
        logging.info(f"Added {len(new_links)} new links for {query} to sheets")

        # Send notifications for links that meet criteria
        total_processed = 0
        total_notified = 0
        for link in new_links:
            if link not in listing_info:
                continue

            total_processed += 1
            info = listing_info[link]
            # Parse the price
            price_value = parse_price(prices[query][link])

            # Check if the price is within the desired range and listing is within 24 hours
            if queries[query]["min_price"] <= price_value <= queries[query]["max_price"] and datetime.now() - info[
                "creation_time"
            ] <= timedelta(hours=24):
                total_notified += 1
                body = (
                    f"{link}\n"
                    f"Title: {info['title']}"
                    f"Price: {prices[query][link]}\n"
                    f"Posted: {info['creation_time'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Location: {info['location']}\n"
                )
                apobj.notify(body=body, title=query)
                time.sleep(3)

        logging.info(f"Processed {total_processed} listings, sent {total_notified} notifications for {query}")

    # Close the browser
    scraper.close()


if __name__ == "__main__":
    main()
