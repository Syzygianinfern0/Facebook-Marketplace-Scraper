import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()

# Open the website
driver.get("https://www.facebook.com/marketplace/austin")


def random_sleep():
    time.sleep(random.randint(1, 3))


def click_close_button():
    close_button = driver.find_element(By.XPATH, "//div[@aria-label='Close']")
    close_button.click()


click_close_button()

# Search for dining table set
random_sleep()
search_box = driver.find_element(By.XPATH, '//input[@placeholder="Search Marketplace"]')
random_sleep()
search_box.send_keys("Dining table set")
random_sleep()
search_box.send_keys(Keys.ENTER)

# Scroll down
driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
time.sleep(3)

# Get all the links
links = driver.find_elements(By.TAG_NAME, "a")
cleaned_links = []
for link in links:
    href = link.get_attribute("href")
    if href and href.startswith("https://www.facebook.com/marketplace/item/"):
        cleaned_links.append(href.split("?")[0])

# Print the links
print(f"Found {len(cleaned_links)} links")
print("Links:")
for link in cleaned_links:
    print(link)
