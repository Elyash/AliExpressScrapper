"""This module is responsible about the scrapping process.
It gets a GiftRequest message from gift_requests RabbitMQ ->
It scrapes the data from the web page into Gift new class ->
It stores the gift in MongoDB ->
It sends back the GiftRequest to scrapped_gifts queue. 
"""

import json
import time

import pika

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from ..Utils import interfaces, models


class AliExpressScrapper:
    """AliExpress Scrapper."""

    def __init__(self):

        # Set up Chrome options (headless mode is optional)
        self.__options__ = Options()
        self.__options__.add_argument('--no-sandbox')
        self.__options__.add_argument('--headless')  # Optional: Remove this to see the browser window
        self.__options__.add_argument('--disable-dev-shm-usage')

        # Set up the WebDriver service
        self.__service__ = Service(ChromeDriverManager().install())

        # Initialize the Chrome WebDriver
        self.__driver__ = webdriver.Chrome(
            service=self.__service__, options=self.__options__
        )

    def __del__(self):
        """Closes resources."""

        # Close the WebDriver
        self.__driver__.quit()

    def scrape_product(self, gift_request: models.GiftRequest) -> models.Gift:
        """Get details about the product by scrapping its web page."""

        gift_details = dict()

        # Go to the AliExpress product page (replace with the product URL)
        self.__driver__.get(gift_request.link)

        # Wait for the page to fully load
        time.sleep(2)  # Adjust this based on your network speed

        # Extract the gift title
        try:
            gift_details['gift_name'] = self.__driver__.find_element(
                By.CLASS_NAME, 'title--wrap--UUHae_g'
            ).text
        except exceptions.InvalidSelectorException as e:
            print('Invalid class name:', e)
        except exceptions.NoSuchElementException as e:
            print('Element not found:', e)

        # Extract the product price
        try:
            gift_details['gift_price'] = self.__driver__.find_element(
                By.XPATH, "//div[@class='price--current--I3Zeidd product-price-current']"
            ).text
        except exceptions.InvalidSelectorException as e:
            print('Invalid class name:', e)
        except exceptions.NoSuchElementException as e:
            print('Element not found:', e)

        # Extract the product main image, TODO: Extract all images.
        try:
            gift_details['gift_images'] = list()
            gift_details['gift_images'].append(self.__driver__.find_element(
                By.XPATH, "//img[@class='magnifier--image--EYYoSlr magnifier--zoom--RzRJGZg']"
            ).get_attribute('src'))
        except exceptions.InvalidSelectorException as e:
            print('Invalid class name:', e)
        except exceptions.NoSuchElementException as e:
            print('Element not found:', e)

        return models.Gift(
            name=gift_details['gift_name'],
            link=gift_request.link,
            description='', # TODO: add scrapping description
            images=gift_details['gift_images'],
            price=gift_details['gift_price'],
            email=gift_request.email
        )


class GiftRequestsConsumerReactor(interfaces.ConsumerReactorRabbitMQI):
    """A reactor that consuming from RabbitMQ and store in mongoDB."""

    def __init__(self, scrapper, mongo_dbi) -> None:
        super().__init__()

        self.__scrapper__ = scrapper
        self.__mongo_dbi__ = mongo_dbi

        # Declare the queue (make sure the queue exists)
        self.__channel__.queue_declare(queue='gift_requests_queue')

        self.__channel__.basic_consume(
            queue='gift_requests_queue', on_message_callback=self.handler, auto_ack=True
        )

    def handler(self, ch, method, properties, body):
        """A callback upon each new gift request in queue."""

        gift_request = models.GiftRequest(**json.loads(body))

        gift = self.__scrapper__.scrape_product(gift_request)
        self.__mongo_dbi__.store_gift(gift)

        self.__channel__.basic_publish(
            exchange='', routing_key='scrapped_gifts_queue', body=body
        ) # TODO: make this OOP

        print(gift) # TODO: remove this and add a lot of logging messages.


# Usage axample
if __name__ == '__main__':
    #example_url = 'https://he.aliexpress.com/item/1005005956410553.html?spm=a2g0o.best.moretolove.2.225c216f6uZIzX&_gl=1*sq3u1s*_gcl_aw*R0NMLjE3MjEyMzcyMjMuQ2p3S0NBancxOTIwQmhBM0Vpd0FKVDNsU2JTeVVqV0dKc05YQzZEWE5GbGZlQ3pUTUZBVDhBZHl1YUJJNXR1bzVuTXV2V3lTUlo4cGNob0N6MGdRQXZEX0J3RQ..*_gcl_dc*R0NMLjE3MjEyMzcyMjMuQ2p3S0NBancxOTIwQmhBM0Vpd0FKVDNsU2JTeVVqV0dKc05YQzZEWE5GbGZlQ3pUTUZBVDhBZHl1YUJJNXR1bzVuTXV2V3lTUlo4cGNob0N6MGdRQXZEX0J3RQ..*_gcl_au*MTk1NTk3NDA2My4xNzI3MDk5Nzcz*_ga*NzI1NjAxMTM1LjE2ODA4MDkyNDg.*_ga_VED1YSGNC7*MTcyNzE4MTU0MC4yMS4xLjE3MjcxODE1NzEuMjkuMC4w&gatewayAdapt=glo2isr'

    aliexpress_scrapper = AliExpressScrapper()
    gifts_dbi = interfaces.GiftsMongoDBI()

    GiftRequestsConsumerReactor(aliexpress_scrapper, gifts_dbi).loop()
