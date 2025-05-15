import asyncio
import aiohttp
import async_timeout
import time
import itertools
import json
import logging
import requests 
from bs4 import BeautifulSoup
from pathlib import Path

# CONFIGURATIONS
ARCHIVE_URL = "https://pastebin.com/archive"
RAW_URL_FMT = "https://pastebin.com/raw/{paste_id}"
OUTPUT_FILE = "keyword_matches.jsonl"


KEYWORDS = [
    "crypto", "bitcoin", "ethereum", "blockchain","t.me"
]

# Maximum paste IDs to scrape
MAX_PASTES = 30

# Rate limiting: max requests per second
RATE_LIMIT = 1.0  # seconds between requests

# Proxy list (HTTP(S) proxies)
PROXIES = [
    # proxy1,
    # proxy2,
]
proxy_cycle = itertools.cycle(PROXIES) if PROXIES else itertools.cycle([None])

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("pastebin_scraper")

### RATE LIMITER ###

class RateLimiter:
    def __init__(self, min_interval: float):
        self.min_interval = min_interval
        self.last = 0.0

    async def wait(self):
        elapsed = time.perf_counter() - self.last
        wait_for = self.min_interval - elapsed
        if wait_for > 0:
            await asyncio.sleep(wait_for)
        self.last = time.perf_counter()


def fetch_latest_paste_ids(max_count=MAX_PASTES):
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(ARCHIVE_URL, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    ids = []
    for a in soup.select("table.maintable a"):
        href = a.get("href", "")
        if href.startswith("/") and len(href.strip("/")) == 8:
            pid = href.strip("/")
            if pid not in ids:
                ids.append(pid)
        if len(ids) >= max_count:
            break
    logger.info(f"Fetched {len(ids)} paste IDs from archive")
    return ids


### STEP 2–4: Async fetch, filter, and write matches ###

async def process_paste(session, rate_limiter, paste_id, out_fh):
    await rate_limiter.wait()
    proxy = next(proxy_cycle)
    raw_url = RAW_URL_FMT.format(paste_id=paste_id)
    try:
        with async_timeout.timeout(15):
            async with session.get(raw_url, proxy=proxy) as resp:
                text = await resp.text()
    except Exception as e:
        logger.warning(f"[{paste_id}] fetch error: {e}")
        return

    found = [kw for kw in KEYWORDS if kw.lower() in text.lower()]
    logger.info(f"[{paste_id}] checked — found keywords: {found}")

    if found:
        record = {
            "source": "pastebin",
            "context": f"Found {', '.join(found)} content in Pastebin paste ID {paste_id}",
            "paste_id": paste_id,
            "url": raw_url,
            "discovered_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "keywords_found": found,
            "status": "pending"
        }
        out_fh.write(json.dumps(record) + "\n")
        logger.info(f"[{paste_id}] MATCH written")


async def main():
    paste_ids = fetch_latest_paste_ids()

    rate_limiter = RateLimiter(RATE_LIMIT)
    connector = aiohttp.TCPConnector(limit=10)  # concurrent connections
    timeout = aiohttp.ClientTimeout(total=20)

    Path(OUTPUT_FILE).unlink(missing_ok=True)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # Open output once for all writes
        with open(OUTPUT_FILE, "a", encoding="utf-8") as out_fh:
            tasks = [
                process_paste(session, rate_limiter, pid, out_fh)
                for pid in paste_ids
            ]
            await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())

