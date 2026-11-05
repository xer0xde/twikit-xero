"""
twikit-xero — X API wrapper with browser-grade TLS.

Fork of d60/twikit with:
- curl_cffi transport (bypasses Cloudflare TLS fingerprinting)
- Precomputed pair dictionary for transaction IDs (replaces broken ondemand.s)
- Resilient parsers (safe field access throughout)
"""

__version__ = '3.0.0'

import asyncio
import os

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Activate browser-grade TLS before any httpx client is created.
from .transport import install as _install_transport
_install_transport()

from ._captcha import Capsolver
from .bookmark import BookmarkFolder
from .errors import *
from .utils import build_query
from .client.client import Client
from .community import Community, CommunityCreator, CommunityMember, CommunityRule
from .geo import Place
from .group import Group, GroupMessage
from .list import List
from .message import Message
from .notification import Notification
from .trend import Trend
from .tweet import CommunityNote, Poll, ScheduledTweet, Tweet
from .user import User
