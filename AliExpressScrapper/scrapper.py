"""This module is responsible about the scrapping process.
It gets a GiftRequest message from gift_requests RabbitMQ ->
It scrapes the data from the web page into Gift new class ->
It stores the gift in MongoDB ->
It sends back the GiftRequest to scrapped_gifts queue. 
"""

import logging
import time
import bson
import json
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from Utils import models, interfaces


# Set up the WebDriver service
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--headless')  # Optional: Remove this to see the browser window
options.add_argument('--disable-dev-shm-usage')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)


# Function to scrap gift details (implement this function)
def scrap_gift(link):

    gift_details = {}
    # Go to the AliExpress product page (replace with the product URL)
    driver.get(link)

    # Wait for the page to fully load
    time.sleep(2)  # Adjust this based on your network speed

    # Extract the gift title
    try:
        gift_details['gift_name'] = driver.find_element(
            By.CLASS_NAME, 'title--wrap--UUHae_g'
        ).text
    except exceptions.InvalidSelectorException as e:
        print('Invalid class name:', e)
    except exceptions.NoSuchElementException as e:
        print('Element not found:', e)

    # Extract the product price
    try:
        gift_details['gift_price'] = driver.find_element(
            By.XPATH, "//div[@class='price--current--I3Zeidd product-price-current']"
        ).text
    except exceptions.InvalidSelectorException as e:
        print('Invalid class name:', e)
    except exceptions.NoSuchElementException as e:
        print('Element not found:', e)

    # Extract the product main image, TODO: Extract all images.
    try:
        gift_details['gift_image'] = driver.find_element(
            By.XPATH, "//div[@class='slider--img--K0YbWW2 slider--active--ETznpbf']"
        ).find_element(By.TAG_NAME, 'img').get_attribute('src')
    except exceptions.InvalidSelectorException as e:
        print('Invalid class name:', e)
    except exceptions.NoSuchElementException as e:
        print('Element not found:', e)

    return gift_details

# Callback function to process GiftRequest messages
def process_gift_request(ch, method, properties, body):
    gift_id = bson.ObjectId(body)
    gift = interfaces.mongo_dbi.get_gift_by_id(gift_id)

    # Scrape gift details from the link
    logging.info('Got a new link to scrape: (link: %s)', gift.link)
    gift_details = scrap_gift(gift.link)
    
    # Update the Gift object with the scraped data
    interfaces.mongo_dbi.update_gift(gift_id, **gift_details)
    
    # Publish a GiftResponse message to the 'gift_responses_queue'
    interfaces.rabbitmq_dbi.publish_scrape_gift_response(gift_id)


# Consume messages from 'gift_requests_queue'
interfaces.rabbitmq_dbi.channel.basic_consume(
    queue='gift_requests_queue',
    on_message_callback=process_gift_request,
    auto_ack=True
)

print('Waiting for GiftRequest messages...')
interfaces.rabbitmq_dbi.channel.start_consuming()
