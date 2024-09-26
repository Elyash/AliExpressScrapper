"""Main connection and interfaces module."""

import dataclasses

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

    def fetch_user(self, email: str) -> models.User:
        """Fetch a user details be email."""

        return models.User(
            **(super().fetch(UsersMongoDBI.COLLECTION_NAME, 'email', email))
        )

    def validate_user(self, user: models.User) -> bool:
        """Validate the user exists and the password is correct."""

        fetched_user = self.fetch_user(user)

        if fetched_user is None:
            raise models.UserNotExistsException(user)

        return user == fetched_user


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
