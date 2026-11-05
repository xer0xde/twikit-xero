# twikit-xero

X (Twitter) API wrapper with browser-grade TLS. Fork of [d60/twikit](https://github.com/d60/twikit).

## What's different

- **Browser TLS fingerprint** — All HTTP requests go through `curl_cffi` with Chrome impersonation. Cloudflare can't tell the difference from a real browser.
- **Pair dictionary for transaction IDs** — Uses [fa0311's precomputed pairs](https://github.com/fa0311/x-client-transaction-id-pair-dict) instead of parsing X's now-defunct `ondemand.s` bundle.
- **Resilient parsers** — Safe field access throughout. No more `KeyError` crashes when X changes their API response format.
- **No Js2Py dependency** — Removed the heavy Js2Py requirement that was only needed for the old ondemand.s approach.

## Install

```bash
pip install git+https://github.com/xer0xde/twikit-xero.git
```

## Usage

```python
import asyncio
from twikit import Client

async def main():
    client = Client('de-DE')

    # Load cookies from a previous browser session
    client.load_cookies('cookies.json')

    # Search tweets
    results = await client.search_tweet('DAX insider', 'Latest', count=10)
    for tweet in results:
        print(f'@{tweet.user.screen_name}: {tweet.text}')

    # Get user info
    user = await client.get_user_by_screen_name('elonmusk')
    print(f'{user.name} has {user.followers_count} followers')

asyncio.run(main())
```

### Getting cookies

The X login API is blocked for non-browser clients (error 366). Export your session cookies from Chrome DevTools:

1. Log into X in Chrome
2. Open DevTools → Application → Cookies → x.com
3. Copy `auth_token`, `ct0`, and `twid` values
4. Save as JSON:

```json
{
  "auth_token": "your_auth_token",
  "ct0": "your_ct0_token",
  "twid": "your_twid"
}
```

## License

MIT — same as the original twikit.
