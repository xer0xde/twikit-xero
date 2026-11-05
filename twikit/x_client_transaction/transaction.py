"""X client transaction ID generation.

Uses fa0311's precomputed pair dictionary instead of parsing
X's now-defunct ondemand.s bundle. The dictionary is updated
multiple times daily by CI at:
https://github.com/fa0311/x-client-transaction-id-pair-dict
"""
import math
import time
import random
import base64
import hashlib
from typing import List

from .utils import base64_encode

PAIR_URL = (
    "https://raw.githubusercontent.com/"
    "fa0311/x-client-transaction-id-pair-dict/refs/heads/main/pair.json"
)

_pair_cache: list | None = None


def _fetch_pairs() -> list:
    """Fetch and cache the precomputed (verification, animationKey) pairs."""
    global _pair_cache
    if _pair_cache is None:
        try:
            from curl_cffi.requests import get
            resp = get(PAIR_URL, impersonate="chrome", timeout=20)
        except ImportError:
            import httpx
            resp = httpx.get(PAIR_URL, timeout=20)
        resp.raise_for_status()
        _pair_cache = resp.json()
    return _pair_cache


class ClientTransaction:
    ADDITIONAL_RANDOM_NUMBER = 3
    DEFAULT_KEYWORD = "obfiowerehiring"

    def __init__(self):
        self.home_page_response = None
        self.key = None
        self.key_bytes = None
        self.animation_key = None

    async def init(self, session, headers):
        """Initialize transaction keys from the pair dictionary."""
        pairs = _fetch_pairs()
        pair = random.choice(pairs)

        self.key = pair["verification"]
        self.key_bytes = list(base64.b64decode(self.key.encode()))
        self.animation_key = pair["animationKey"]
        self.home_page_response = True

    def get_key_bytes(self, key: str) -> List[int]:
        return list(base64.b64decode(bytes(key, 'utf-8')))

    def generate_transaction_id(
        self, method: str, path: str, response=None,
        key=None, animation_key=None, time_now=None
    ) -> str:
        time_now = time_now or math.floor(
            (time.time() * 1000 - 1682924400 * 1000) / 1000)
        time_now_bytes = [(time_now >> (i * 8)) & 0xFF for i in range(4)]
        key = key or self.key
        if key is None:
            raise RuntimeError(
                "Transaction not initialized. Call init() first or load cookies."
            )
        key_bytes = self.get_key_bytes(key)
        animation_key = animation_key or self.animation_key
        hash_val = hashlib.sha256(
            f"{method}!{path}!{time_now}{self.DEFAULT_KEYWORD}{animation_key}"
            .encode()
        ).digest()
        hash_bytes = list(hash_val)
        random_num = random.randint(0, 255)
        bytes_arr = [
            *key_bytes, *time_now_bytes,
            *hash_bytes[:16], self.ADDITIONAL_RANDOM_NUMBER
        ]
        out = bytearray(
            [random_num, *[item ^ random_num for item in bytes_arr]])
        return base64_encode(out).strip("=")
