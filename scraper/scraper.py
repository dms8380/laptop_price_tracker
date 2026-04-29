"""
scraper.py
----------
Scrapes laptop data from:
    https://webscraper.io/test-sites/e-commerce/static/computers/laptops

This site is purpose-built for web scraping practice. It is plain static
HTML (no JavaScript rendering required), never blocks bots, and contains
real-looking laptop names, prices, and ratings across multiple pages.
"""

import requests
from bs4 import BeautifulSoup
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BASE_URL  = "https://webscraper.io"
START_URL = "https://webscraper.io/test-sites/e-commerce/static/computers/laptops"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _parse_price(text: str) -> float:
    """Convert a price string like '$299.99' to a float."""
    try:
        return round(float(text.replace("$", "").replace(",", "").strip()), 2)
    except (ValueError, AttributeError):
        return 0.0


def _parse_rating(card) -> float:
    """Extract star rating from the number of filled star elements (0–5)."""
    try:
        stars = card.select("div.ratings span.glyphicon-star:not(.glyphicon-star-empty)")
        return float(len(stars))
    except Exception:
        return 0.0


def _scrape_page(url: str) -> tuple[list[dict], str | None]:
    """
    Fetch one page of laptop listings.

    Returns:
        (list of laptop dicts, next_page_url or None)
    """
    laptops = []

    try:
        response = requests.get(url, headers=HEADERS, timeout=12)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return laptops, None

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select("div.thumbnail")
    logger.info(f"Found {len(cards)} product cards on {url}")

    for card in cards:
        try:
            name_el  = card.select_one("a.title")
            price_el = card.select_one("h4.price")

            if not name_el or not price_el:
                continue

            name  = name_el.get("title", name_el.text).strip()
            price = _parse_price(price_el.text)

            if not name or price == 0.0:
                continue

            rating = _parse_rating(card)

            laptops.append({
                "name":      name,
                "price":     price,
                "price_str": f"${price:,.2f}",
                "rating":    rating,
            })

        except Exception as e:
            logger.warning(f"Skipped a card: {e}")
            continue

    # Pagination — find the "next" button
    next_url = None
    next_btn = soup.select_one("a[rel='next']") or soup.select_one("li.next a")
    if next_btn and next_btn.get("href"):
        href = next_btn["href"]
        next_url = href if href.startswith("http") else BASE_URL + href

    return laptops, next_url


def scrape_laptops(max_pages: int = 5) -> list[dict]:
    """
    Scrape up to max_pages pages of laptops from the test site.

    Args:
        max_pages: Maximum number of pages to scrape (default 5).

    Returns:
        List of laptop dicts with keys: name, price, price_str, rating.
    """
    all_laptops: list[dict] = []
    url = START_URL

    for page_num in range(1, max_pages + 1):
        logger.info(f"Scraping page {page_num}: {url}")
        laptops, next_url = _scrape_page(url)
        all_laptops.extend(laptops)

        if not next_url:
            logger.info("No more pages found.")
            break

        url = next_url
        time.sleep(0.5)  # be polite

    logger.info(f"Total laptops scraped: {len(all_laptops)}")
    return all_laptops
