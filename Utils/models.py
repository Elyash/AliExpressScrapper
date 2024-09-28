"""Project models."""
import dataclasses


@dataclasses.dataclass
class User:
    """A user in the web app."""

    name: str
    email: str
    password: str


@dataclasses.dataclass
class GiftRequest:
    """A gift scrapping request."""

    link: str
    user_email: str

@dataclasses.dataclass
class Gift:
    """A Gift (as saved at DB)."""

    user_email: str
    link: str
    gift_name: str
    gift_price: str
    gift_image: str
