"""Main connection and interfaces module."""

from typing import Any

import dataclasses

import json
import pika
import pymongo

from . import models


class MongoDBI:
    """An interface to connect with mongoDB."""

    DB_NAME: str = 'MyFullstackProject'

    def __init__(self):
        self.__client__ = pymongo.MongoClient(
            "mongodb", port=27017, username='admin', password='password'
        )

    def __del__(self):
        self.__client__.close()

    def store(self, collection: str, record: dict[str, str]) -> None:
        """Insert new document to MongoDB."""

        self.__client__[MongoDBI.DB_NAME][collection].insert_one(record)  # TODO: check the reutrn value
        
    def fetch(self, collection: str, key: str, value: str) -> dict:
        """Fetch a document from MongoDB."""

        return self.__client__[MongoDBI.DB_NAME][collection].find_one({key: value})

    def remove(self, collection: str, key: str, value: str) -> None:
        """Deletes a document from MongoDB."""

        self.__client__[MongoDBI.DB_NAME][collection].find_one_and_delete({key: value})


class UsersMongoDBI(MongoDBI):
    """An interface to connect with Users table in mongoDB."""

    COLLECTION_NAME = 'Users'

    def store_user(self, user: models.User):
        """Store a new user in the DB."""

        self.store(UsersMongoDBI.COLLECTION_NAME, dataclasses.asdict(user))

    def fetch_user(self, email: str) -> models.User | None:
        """Fetch a user details be email."""

        fetched_user = super().fetch(UsersMongoDBI.COLLECTION_NAME, 'email', email)

        return models.User(**fetched_user) if fetched_user else None


class GiftsMongoDBI(MongoDBI):
    """An interface to connect with Gifts table in mongoDB."""

    COLLECTION_NAME = 'Gifts'

    def add_gift(self, gift: models.Gift) -> None:
        """Store a new gift in the DB."""

        self.store(GiftsMongoDBI.COLLECTION_NAME, dataclasses.asdict(gift))

    def fetch_gift(self, gift_name: str) -> models.Gift:
        """Fetch a Gift details be username."""

        return models.Gift(
            **(super().fetch(GiftsMongoDBI.COLLECTION_NAME, 'name', gift_name))
        )

    def remove_gift(self, gift_name: str) -> None:
        """Removes a gift from the DB."""

        super().remove(GiftsMongoDBI.COLLECTION_NAME, 'name', gift_name)

    def fetch_gifts_for_user(self, email: str) -> list[models.Gift]:
        """Fetch all gifts of user by its email."""

        return self.__client__[MongoDBI.DB_NAME][GiftsMongoDBI.COLLECTION_NAME].find(
            {'email': email}
        )


class RabbitMQI:
    """An interface to communicate with RabbitMQ."""
    def __init__(self):
        """Starts a connectinon with RabbitMQ."""

        connection_params = pika.ConnectionParameters(
            host='rabbitmq',
            port=5672,
            credentials=pika.PlainCredentials(
                username='user', password='password'
            )
        )
        # TODO: Add to docker-compose to wait.
        self.__connection__ = pika.BlockingConnection(connection_params)
        self.__channel__ = self.__connection__.channel()

    def __del__(self):
        """Closes the RabbitMQ communication."""

        self.__connection__.close()


class PublisherRabbitMQI(RabbitMQI):
    """RabbitMQ interface for publisher."""

    def publish(self, queue_name: str, message: str) -> None:
        """Publish a new message to queue."""

        self.__channel__.basic_publish(
            exchange='', routing_key=queue_name, body=message
        )


class ConsumerReactorRabbitMQI(RabbitMQI):
    """RabbitMQ interface for consuming messages."""

    def loop(self):
        """Consuming and proccessing loop."""

        self.__channel__.start_consuming()

    def handler(self, ch, method, properties, body):
        """A callback upon each message in the links queue."""

        raise NotImplementedError()



class GiftRequestsPubliserRabbitMQI(PublisherRabbitMQI):
    """RabbitMQ interface for publish gift requests."""

    QUEUE = 'gift_requests'

    def publish_gift_request(self, gift_request: models.GiftRequest) -> None:
        """Publish a gift request to its queue."""

        message = json.dumps(dataclasses.asdict(gift_request))
        super().publish(GiftRequestsPubliserRabbitMQI.QUEUE, message)
