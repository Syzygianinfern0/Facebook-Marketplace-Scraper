import logging
import random
import time

import apprise
import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from sheets import Sheets


def random_sleep():
    time.sleep(random.randint(1, 3))


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
        self.driver.get(f"https://www.facebook.com/marketplace/austin/search/?query={query}")
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
    for query in queries:
        links[query], prices[query] = scraper.get_listings(query)
        random_sleep()

    # Close the browser
    scraper.close()

    # Check if the links are new
    for query, new_links in links.items():
        old_links = sheets.get_links(query)
        new_links = [link for link in new_links if link not in old_links]
        sheets.update_links(query, new_links)
        # print(f"Added {len(new_links)} new links for {query}")
        logging.info(f"Added {len(new_links)} new links for {query}")
        for link in new_links:
            body = f"{link}\nPrice: {prices[query][link]}"
            apobj.notify(body=body, title=query)


if __name__ == "__main__":
    main()
