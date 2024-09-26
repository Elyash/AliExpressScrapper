"""Main models module."""

import dataclasses

# TODO: work not with aliexpress pages
@dataclasses.dataclass
class Gift:
    """All of the scraping data from the web page."""

    name: str # Primary key
    link: str | None
    description: str | None
    images: list[str] # Main image in images[0]
    price: int | None
    email: str # The email of the user the gift belongs

@dataclasses.dataclass
class User:
    """A user in the gift app."""

    email: str # Primary key
    first_name: str
    password: str


class UserNotExistsException(Exception):
    """The user not found in the DB."""

    def __init__(self, user):
        self.user: User = user

    def __str__(self):
        return f'User not found: (email: {self.user.email})'

