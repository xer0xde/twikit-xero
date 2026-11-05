from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Literal

from ..utils import Result, timestamp_to_datetime

if TYPE_CHECKING:
    from .client import GuestClient
    from .tweet import Tweet


class User:
    """Represents an X (Twitter) user profile (guest context)."""

    def __init__(self, client: GuestClient, data: dict) -> None:
        self._client = client
        legacy = data.get('legacy', {})
        entities = legacy.get('entities', {})

        self.id: str = data.get('rest_id', '')
        self.created_at: str = legacy.get('created_at', '')
        self.name: str = legacy.get('name', '')
        self.screen_name: str = legacy.get('screen_name', '')
        self.profile_image_url: str = legacy.get('profile_image_url_https', '')
        self.profile_banner_url: str | None = legacy.get('profile_banner_url')
        self.url: str | None = legacy.get('url')
        self.location: str = legacy.get('location', '')
        self.description: str = legacy.get('description', '')
        self.description_urls: list = entities.get('description', {}).get('urls', [])
        self.urls: list = entities.get('url', {}).get('urls', [])
        self.pinned_tweet_ids: list[str] = legacy.get('pinned_tweet_ids_str', [])
        self.is_blue_verified: bool = data.get('is_blue_verified', False)
        self.verified: bool = legacy.get('verified', False)
        self.possibly_sensitive: bool = legacy.get('possibly_sensitive', False)
        self.default_profile: bool = legacy.get('default_profile', False)
        self.default_profile_image: bool = legacy.get('default_profile_image', False)
        self.has_custom_timelines: bool = legacy.get('has_custom_timelines', False)
        self.followers_count: int = legacy.get('followers_count', 0)
        self.fast_followers_count: int = legacy.get('fast_followers_count', 0)
        self.normal_followers_count: int = legacy.get('normal_followers_count', 0)
        self.following_count: int = legacy.get('friends_count', 0)
        self.favourites_count: int = legacy.get('favourites_count', 0)
        self.listed_count: int = legacy.get('listed_count', 0)
        self.media_count: int = legacy.get('media_count', 0)
        self.statuses_count: int = legacy.get('statuses_count', 0)
        self.is_translator: bool = legacy.get('is_translator', False)
        self.translator_type: str = legacy.get('translator_type', '')
        self.withheld_in_countries: list[str] = legacy.get('withheld_in_countries', [])
        self.protected: bool = legacy.get('protected', False)

    @property
    def created_at_datetime(self) -> datetime:
        return timestamp_to_datetime(self.created_at)

    async def get_tweets(
        self, tweet_type: Literal['Tweets'] = 'Tweets', count: int = 40
    ) -> list[Tweet]:
        """Retrieves the user's tweets."""
        return await self._client.get_user_tweets(self.id, tweet_type, count)

    async def get_highlights_tweets(
        self, count: int = 20, cursor: str | None = None
    ) -> Result[Tweet]:
        """Retrieves highlighted tweets from the user's timeline."""
        return await self._client.get_user_highlights_tweets(self.id, count, cursor)

    async def update(self) -> None:
        new = await self._client.get_user_by_id(self.id)
        self.__dict__.update(new.__dict__)

    def __repr__(self) -> str:
        return f'<User id="{self.id}">'

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, User) and self.id == __value.id

    def __ne__(self, __value: object) -> bool:
        return not self == __value
