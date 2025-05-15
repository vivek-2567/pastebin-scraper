# Pastebin Crypto Scraper

## Overview

This project is a Pastebin scraper that fetches the latest 30 paste IDs from the Pastebin archive, retrieves their raw content asynchronously, filters the content by specific cryptocurrency-related keywords, and writes the matching results to a JSON Lines file (`keyword_matches.jsonl`).

### Features

- Scrapes the latest 30 paste IDs from Pastebin archive.
- Fetches raw paste content asynchronously for improved concurrency.
- Filters pastes by keywords related to cryptocurrency and blockchain.
- Writes matched pastes to a JSON Lines file with relevant metadata.
- Implements rate limiting to ensure a maximum of 1 request per second.
- Supports proxy rotation for requests (optional).
- Logs the scraping process, including checks and matches.

## Keywords Filtered

- crypto
- bitcoin
- ethereum
- blockchain
- t.me

## How It Works

1. Fetches the latest 30 paste IDs from the Pastebin archive page.
2. Asynchronously fetches the raw content of each paste using aiohttp.
3. Applies rate limiting to avoid exceeding 1 request per second.
4. Optionally rotates through a list of HTTP(S) proxies for requests.
5. Checks if the paste content contains any of the specified keywords.
6. Writes matching pastes to `keyword_matches.jsonl` with metadata including paste ID, URL, keywords found, and timestamp.
7. Logs the progress and any errors encountered during scraping.

## Requirements

- Python 3.7+
- `aiohttp`
- `async_timeout`
- `requests`
- `beautifulsoup4`

You can install the required packages using pip:

```bash
pip install -r requirements.txt
```

## Usage

1. Clone or download this repository.
2. (Optional) Update the `PROXIES` list in `scrape.py` if you want to use proxy rotation.
3. Run the scraper:

```bash
python scrape.py
```

4. The script will create or overwrite the file `keyword_matches.jsonl` in the current directory with the matched paste data.

## Notes

- The script respects rate limiting to avoid overwhelming Pastebin servers.
- Proxy rotation is optional and can be configured by adding proxy URLs to the `PROXIES` list.
- Logging output is printed to the console to track progress and issues.
- The output file is in JSON Lines format, where each line is a JSON object representing a matched paste.

## License

This project is licensed under the [MIT License](LICENSE). 
This project is provided as-is without any warranty. Use responsibly and respect Pastebin's terms of service.