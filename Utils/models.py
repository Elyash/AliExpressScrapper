"""Main models module."""

import dataclasses

import bson

import flask_login

# TODO: work not with aliexpress pages
@dataclasses.dataclass
class Gift:
    """All of the scraping data from the web page."""

    name: str # Primary key
    link: str | None
    price: int | None
    email: str # The email of the user the gift belongs
    description: str | None = None
    images: list[str] | None = None # Main image in images[0]

@dataclasses.dataclass
class GiftRequest:
    """Link for gift and the user's email."""

    link: str
    email: str # The email of the user the gift belongs


@dataclasses.dataclass
class User(flask_login.UserMixin):
    """A user in the gift app."""

    _id: bson.ObjectId  # For flask_login usage
    email: str # Primary key
    first_name: str
    password: str
    _id: bson.ObjectId  # For flask_login usage

    def get_id(self) -> bson.ObjectId | None:
        """Gets the user flask_login ID."""

        return self._id


class UserNotExistsException(Exception):
    """The user not found in the DB."""

    def __init__(self, user):
        self.user: User = user

    def __str__(self):
        return f'User not found: (email: {self.user.email})'

