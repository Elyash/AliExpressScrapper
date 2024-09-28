"""Project main interfaces."""

import json
import time

import pika
import pymongo

from Utils import models


class MongoDBI:
    """A client interface with MongoDB server."""

    MONGO_DB_CONTAINER: str = 'mongodb'
    MONGO_DB_PORT: int = 27017
    MONGO_DB_USERNAME: str = 'admin'
    MONGO_DB_PASSWORD: str = 'password'

    PROJECT_DB_NAME: str = 'MyFullstackProject'

    def __init__(self):
        self.mongo_client = pymongo.MongoClient(
            host=MongoDBI.MONGO_DB_CONTAINER,
            port=MongoDBI.MONGO_DB_PORT,
            username=MongoDBI.MONGO_DB_USERNAME,
            password=MongoDBI.MONGO_DB_PASSWORD
        )
        self.db = self.mongo_client[MongoDBI.PROJECT_DB_NAME]
        self.gifts_collection = self.db['Gifts']
        self.users_collection = self.db['Users']

    def get_user(self, email: str) -> dict[str, str]:
        """Gets user details by email from DB."""

        return self.users_collection.find_one({"email": email})

    def add_user(self, user: models.User) -> None:
        """Add new user to DB."""

        self.users_collection.insert_one(user.__dict__) 

    def get_gift(self, gift_request: models.GiftRequest) -> dict[str, str]:
        """Gets gift details by gift request from DB."""

        return self.gifts_collection.find_one(
            {"user_email": gift_request.user_email, "link": gift_request.link}
        )

    def add_gift(self, gift: models.Gift) -> None:
        """Adds a new gift to DB."""

        self.gifts_collection.insert_one(gift)


class RabbitMQDBI:
    """A client interface (publisher and consumer) for RabbitMQ."""

    RABBIT_MQ_CONTAINER: str = 'rabbitmq'
    RABBIT_MQ_PORT: int = 5672
    RABBIT_MQ_USERNAME: str = 'user'
    RABBIT_MQ_PASSWORD: str = 'password'

    def __init__(self):
        # Wait for RabbitMQ container to run
        time.sleep(7)
        connection_params = pika.ConnectionParameters(
            host=RabbitMQDBI.RABBIT_MQ_CONTAINER,
            port=RabbitMQDBI.RABBIT_MQ_PORT,
            credentials=pika.PlainCredentials(
                username=RabbitMQDBI.RABBIT_MQ_USERNAME,
                password=RabbitMQDBI.RABBIT_MQ_PASSWORD
            ),
            heartbeat=60,
            retry_delay=5
        )
        self.connection = pika.BlockingConnection(connection_params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='gift_requests_queue')
        self.channel.queue_declare(queue='gift_responses_queue')

    def publish_gift_request(self, gift_request: models.GiftRequest) -> None:
        """Publishes a new gift requests to gift requests queue."""

        self.channel.basic_publish(
            exchange='',
            routing_key='gift_requests_queue',
            body=json.dumps(gift_request.__dict__)
        )


mongo_dbi = MongoDBI()
rabbitmq_dbi = RabbitMQDBI()

