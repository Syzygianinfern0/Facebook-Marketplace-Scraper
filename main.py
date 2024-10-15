import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def random_sleep():
    time.sleep(random.randint(1, 3))


class FacebookMarketplaceScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()

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

        return cleaned_links

    def close(self):
        self.driver.quit()


def main():
    scraper = FacebookMarketplaceScraper()

    # Get the queries
    queries = ["dining table set", "couch", "bed frame"]

    # Get the links
    links = []
    for query in queries:
        links.extend(scraper.get_listings(query))

    # Close the browser
    scraper.close()

    # Print the links
    print(f"Found {len(links)} links")
    print("Links:")
    for link in links:
        print(link)


if __name__ == "__main__":
    main()
