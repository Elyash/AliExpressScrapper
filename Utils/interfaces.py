"""Project main interfaces."""

import bson
import json
import time

import pika
import pymongo
import pymongo.results

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

    def get_user(self, email: str) -> models.User | None:
        """Gets user details by email from DB."""

        result = self.users_collection.find_one({"email": email})

        # Get rid of mongo's inner vars
        if result:
            del result['_id']
            return models.User(**result)
        return result

    def add_user(self, user: models.User) -> pymongo.results.InsertOneResult:
        """Add new user to DB."""

        return self.users_collection.insert_one(user.__dict__)

    def get_gift(self, user_email: str, link: str) -> models.Gift | None:
        """Gets gift by gift from DB."""

        result = self.gifts_collection.find_one(
            {"user_email": user_email, "link": link}
        )

        # Get rid of mongo's inner vars
        if result:
            del result['_id']
            return models.Gift(**result)
        return result

    def get_gift_by_id(self, gift_id: bson.ObjectId) -> models.Gift | None:
        """Gets gift by its mongoDB id."""

        result = self.gifts_collection.find_one({"_id": gift_id})

        # Get rid of mongo's inner vars
        if result:
            del result['_id']
            return models.Gift(**result)
        return result
    
    def get_user_gifts_as_dicts(self, user_email: str) -> list[dict[str, str]]:
        """Gets all user's gifts from DB."""

        return list(self.gifts_collection.find({'user_email': user_email}))

    def delete_gift_by_id(self, gift_id: bson.ObjectId) -> pymongo.results.DeleteResult:
        """Deletes gift by its ID."""

        return self.gifts_collection.delete_one({'_id': gift_id})

    def update_gift(self, gift_id: bson.ObjectId, **kwargs: dict[str, str]
        ) -> pymongo.results.UpdateResult:
        """Updates one or more values in a gift."""

        return self.gifts_collection.update_one(
            filter={"_id": gift_id},
            update={"$set": kwargs}
        )

    def add_gift(self, gift: models.Gift) -> pymongo.results.InsertOneResult:
        """Adds a new gift to DB."""

        return self.gifts_collection.insert_one(gift.__dict__)


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

    def publish_scrape_gift_request(self, gift_id: bson.ObjectId) -> None:
        """Publishes a new gift requests to gift requests queue."""

        self.channel.basic_publish(
            exchange='',
            routing_key='gift_requests_queue',
            body=gift_id.binary
        )

    def publish_scrape_gift_response(self, gift_id: bson.ObjectId) -> None:
        """Publishes a response to gift request."""

        self.channel.basic_publish(
            exchange='',
            routing_key='gift_responses_queue',
            body=gift_id.binary
        )


mongo_dbi = MongoDBI()
rabbitmq_dbi = RabbitMQDBI()

