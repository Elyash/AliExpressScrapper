"""Project models."""

import dataclasses

import bson


@dataclasses.dataclass
class User:
    """A user in the web app."""

    name: str
    email: str
    password: str


@dataclasses.dataclass
class Gift:
    """A Gift (as saved at DB)."""

    user_email: str
    link: str
    gift_name: str | None = None
    gift_price: str | None = None
    gift_image: str | None = None
