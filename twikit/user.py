from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Literal

from .utils import timestamp_to_datetime

if TYPE_CHECKING:
    from httpx import Response

    from .client.client import Client
    from .message import Message
    from .tweet import Tweet
    from .utils import Result


class User:
    """Represents an X (Twitter) user profile."""

    def __init__(self, client: Client, data: dict) -> None:
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
        self.can_dm: bool = legacy.get('can_dm', False)
        self.can_media_tag: bool = legacy.get('can_media_tag', False)
        self.want_retweets: bool = legacy.get('want_retweets', False)
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
        self,
        tweet_type: Literal['Tweets', 'Replies', 'Media', 'Likes'],
        count: int = 40,
    ) -> Result[Tweet]:
        """Retrieves the user's tweets."""
        return await self._client.get_user_tweets(self.id, tweet_type, count)

    async def follow(self) -> Response:
        """Follows the user."""
        return await self._client.follow_user(self.id)

    async def unfollow(self) -> Response:
        """Unfollows the user."""
        return await self._client.unfollow_user(self.id)

    async def block(self) -> Response:
        """Blocks the user."""
        return await self._client.block_user(self.id)

    async def unblock(self) -> Response:
        """Unblocks the user."""
        return await self._client.unblock_user(self.id)

    async def mute(self) -> Response:
        """Mutes the user."""
        return await self._client.mute_user(self.id)

    async def unmute(self) -> Response:
        """Unmutes the user."""
        return await self._client.unmute_user(self.id)

    async def get_followers(self, count: int = 20) -> Result[User]:
        """Retrieves a list of followers for the user."""
        return await self._client.get_user_followers(self.id, count)

    async def get_verified_followers(self, count: int = 20) -> Result[User]:
        """Retrieves a list of verified followers for the user."""
        return await self._client.get_user_verified_followers(self.id, count)

    async def get_followers_you_know(self, count: int = 20) -> Result[User]:
        """Retrieves a list of followers the user might know."""
        return await self._client.get_user_followers_you_know(self.id, count)

    async def get_following(self, count: int = 20) -> Result[User]:
        """Retrieves a list of users the user is following."""
        return await self._client.get_user_following(self.id, count)

    async def get_subscriptions(self, count: int = 20) -> Result[User]:
        """Retrieves a list of users the user is subscribed to."""
        return await self._client.get_user_subscriptions(self.id, count)

    async def get_latest_followers(
        self, count: int | None = None, cursor: str | None = None
    ) -> Result[User]:
        """Retrieves the latest followers. Max count: 200."""
        return await self._client.get_latest_followers(
            self.id, count=count, cursor=cursor
        )

    async def get_latest_friends(
        self, count: int | None = None, cursor: str | None = None
    ) -> Result[User]:
        """Retrieves the latest friends (following). Max count: 200."""
        return await self._client.get_latest_friends(
            self.id, count=count, cursor=cursor
        )

    async def send_dm(
        self, text: str, media_id: str = None, reply_to=None
    ) -> Message:
        """Send a direct message to the user."""
        return await self._client.send_dm(self.id, text, media_id, reply_to)

    async def get_dm_history(self, max_id: str = None) -> Result[Message]:
        """Retrieves the DM conversation history with the user."""
        return await self._client.get_dm_history(self.id, max_id)

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
