"""This module is responsible about the scrapping process.
It gets a GiftRequest message from gift_requests RabbitMQ ->
It scrapes the data from the web page into Gift new class ->
It stores the gift in MongoDB ->
It sends back the GiftRequest to scrapped_gifts queue. 
"""

import logging
import time
import pika
import json
from pymongo import MongoClient
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from Utils import models


# MongoDB setup
mongo_client = MongoClient("mongodb", port=27017, username='admin', password='password')
db = mongo_client['MyFullstackProject']
gifts_collection = db['Gifts']

# Set up the WebDriver service
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--headless')  # Optional: Remove this to see the browser window
options.add_argument('--disable-dev-shm-usage')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# RabbitMQ setup
time.sleep(8)
connection_params = pika.ConnectionParameters(
    host='rabbitmq',
    port=5672,
    credentials=pika.PlainCredentials(
        username='user', password='password'
    ),
    heartbeat=60,
    retry_delay=5
)
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()

# Declare queues
channel.queue_declare(queue='gift_requests_queue')
channel.queue_declare(queue='gift_responses_queue')

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
    gift_request_data = json.loads(body)
    gift_request = models.GiftRequest(user_email=gift_request_data['user_email'], link=gift_request_data['link'])
    
    # Scrape gift details from the link
    logging.info('Got a new link to scrape: (link: %s)', gift_request.link)
    gift_details = scrap_gift(gift_request.link)
    
    # Create a Gift object with the scraped data
    gift = models.Gift(
        user_email=gift_request.user_email,
        link=gift_request.link,
        gift_name=gift_details['gift_name'],
        gift_price=gift_details['gift_price'],
        gift_image=gift_details['gift_image']
    )
    
    # Store the Gift object in the MongoDB "Gifts" collection
    gifts_collection.insert_one(gift.__dict__)
    print(f"Stored Gift in MongoDB: {gift.__dict__}")
    
    # Publish a GiftResponse message to the 'gift_responses_queue'
    gift_response = {
        "user_email": gift.user_email,
        "link": gift.link,
        "gift_name": gift.gift_name,
        "gift_price": gift.gift_price,
        "gift_image": gift.gift_image
    }
    channel.basic_publish(
        exchange='',
        routing_key='gift_responses_queue',
        body=json.dumps(gift_response)
    )
    print(f"Published GiftResponse to RabbitMQ: {gift_response}")

# Consume messages from 'gift_requests_queue'
channel.basic_consume(queue='gift_requests_queue', on_message_callback=process_gift_request, auto_ack=True)

print('Waiting for GiftRequest messages...')
channel.start_consuming()