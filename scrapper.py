
from __future__ import annotations

import argparse
import logging
import re
import sys
import time
import urllib.robotparser as robotparser
from dataclasses import dataclass, asdict
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    print("This script needs pandas + openpyxl: pip install pandas openpyxl")
    sys.exit(1)



# Configuration & logging


BASE_URL = "https://www.shadowfox.org.in"
DEFAULT_PAGES = ["/", "/approach", "/domains", "/merch"]
USER_AGENT = (
    "ShadowFoxPracticeScraper/1.0 "
    "(educational data-extraction exercise; piyushahire12@gmail.com)"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("shadowfox_scraper.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("shadowfox_scraper")


# Data models
@dataclass
class Testimonial:
    name: str
    track: str
    quote: str
    image_url: Optional[str]
    source_page: str

@dataclass
class PartnerInstitution:
    name: str
    logo_url: Optional[str]
    source_page: str

@dataclass
class SiteStat:
    label: str
    raw_value: str
    source_page: str
    note: str = ""

@dataclass
class NavLink:
    section: str  # "header" or "footer"
    text: str
    url: str
    source_page: str



# HTTP layer — retries, backoff, robots.txt compliance


class PoliteSession:
    """A requests.Session wrapped with retry/backoff and robots.txt checks."""

    def __init__(self, base_url: str, user_agent: str, delay_seconds: float = 1.0):
        self.base_url = base_url.rstrip("/")
        self.delay_seconds = delay_seconds
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

        retry_strategy = Retry(
            total=3,
            backoff_factor=1.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.robots = robotparser.RobotFileParser()
        self._load_robots()

    def _load_robots(self) -> None:
        robots_url = urljoin(self.base_url, "/robots.txt")
        try:
            resp = self.session.get(robots_url, timeout=10)
            if resp.status_code == 200:
                self.robots.parse(resp.text.splitlines())
                log.info("Loaded robots.txt from %s", robots_url)
            else:
                log.warning(
                    "robots.txt returned %s — proceeding with default politeness rules",
                    resp.status_code,
                )
                self.robots = None
        except requests.RequestException as exc:
            log.warning("Could not fetch robots.txt (%s) — proceeding cautiously", exc)
            self.robots = None

    def _allowed(self, url: str) -> bool:
        if self.robots is None:
            return True
        try:
            return self.robots.can_fetch(self.session.headers["User-Agent"], url)
        except Exception:  # pragma: no cover — never let robots parsing crash a run
            return True

    def get(self, path: str) -> Optional[BeautifulSoup]:
        """Fetch a path relative to base_url and return parsed soup, or None on failure."""
        url = urljoin(self.base_url + "/", path.lstrip("/"))

        if not self._allowed(url):
            log.warning("Skipping %s — disallowed by robots.txt", url)
            return None

        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as exc:
            log.error("Failed to fetch %s: %s", url, exc)
            return None

        time.sleep(self.delay_seconds)  # rate limiting, be a good citizen
        return BeautifulSoup(resp.text, "html.parser")


# --------------------------------------------------------------------------- #
# Extractors — each is isolated and failure-tolerant
# --------------------------------------------------------------------------- #

QUOTE_CHARS = "“\"”"


def extract_testimonials(soup: BeautifulSoup, page: str) -> List[Testimonial]:

    results: List[Testimonial] = []
    try:
        headings = soup.find_all(re.compile(r"^h[3-5]$"))
        for heading in headings:
            name = heading.get_text(strip=True)
            if not name or len(name.split()) > 5:
                continue  # unlikely to be a person's name

            # The testimonial photo typically precedes the name heading in
            # the DOM (image -> heading -> track -> quote), so check backward
            # first and only fall back to a forward search if that misses.
            img_url = None
            prev_img = heading.find_previous("img")
            if prev_img is not None:
                img_url = prev_img.get("src")

            # Look at the next few siblings for a short "track" line and a quote
            track, quote = "", ""
            node = heading
            for _ in range(6):
                node = node.find_next(["p", "span", "div", "img"])
                if node is None:
                    break
                if node.name == "img":
                    if img_url is None:
                        img_url = node.get("src")
                    continue
                text = node.get_text(strip=True)
                if not text:
                    continue
                if any(q in text for q in QUOTE_CHARS) and len(text) > 25:
                    quote = text.strip(QUOTE_CHARS + " ")
                    break
                if not track and len(text.split()) <= 4:
                    track = text

            if quote:
                results.append(Testimonial(
                    name=name, track=track, quote=quote,
                    image_url=img_url, source_page=page,
                ))
    except Exception as exc:  # never let one bad card kill the whole scrape
        log.warning("Testimonial extraction hiccup on %s: %s", page, exc)

    log.info("Extracted %d testimonials from %s", len(results), page)
    return results


def extract_partner_institutions(soup: BeautifulSoup, page: str) -> List[PartnerInstitution]:

    results: List[PartnerInstitution] = []
    seen = set()
    try:
        for img in soup.find_all("img"):
            alt = (img.get("alt") or "").strip()
            if not alt or alt.lower() in seen:
                continue
            if re.search(r"logo|university|college|institute|iem|vit|srm", alt, re.I):
                src = img.get("src")
                results.append(PartnerInstitution(name=alt, logo_url=src, source_page=page))
                seen.add(alt.lower())
    except Exception as exc:
        log.warning("Partner-institution extraction hiccup on %s: %s", page, exc)

    log.info("Extracted %d partner institutions from %s", len(results), page)
    return results


def extract_stats(soup: BeautifulSoup, page: str) -> List[SiteStat]:

    results: List[SiteStat] = []
    try:
        candidates = soup.find_all(string=re.compile(r"^\s*\d+[%+]?\s*$"))
        for value_node in candidates:
            value = value_node.strip()
            label_node = value_node.find_next(string=True)
            label = label_node.strip() if label_node else ""
            if not label or label == value:
                continue

            note = ""
            if value in {"0+", "0%", "0"}:
                note = "Likely a JS-animated counter — static fetch sees pre-animation 0"

            results.append(SiteStat(label=label, raw_value=value, source_page=page, note=note))
    except Exception as exc:
        log.warning("Stat extraction hiccup on %s: %s", page, exc)

    log.info("Extracted %d stats from %s", len(results), page)
    return results


def extract_nav_links(soup: BeautifulSoup, page: str) -> List[NavLink]:
    """Pulls links out of <header>/<nav> and <footer> — falls back to the
    first and last link-bearing containers if semantic tags aren't present."""
    results: List[NavLink] = []
    try:
        header = soup.find(["header", "nav"])
        footer = soup.find("footer")

        for section_name, container in (("header", header), ("footer", footer)):
            if container is None:
                continue
            for a in container.find_all("a", href=True):
                text = a.get_text(strip=True)
                href = a["href"]
                if not text or href.startswith("#"):
                    continue
                results.append(NavLink(
                    section=section_name, text=text,
                    url=urljoin(BASE_URL, href), source_page=page,
                ))
    except Exception as exc:
        log.warning("Nav-link extraction hiccup on %s: %s", page, exc)

    log.info("Extracted %d nav links from %s", len(results), page)
    return results

# Orchestration

class ShadowFoxScraper:
    def __init__(self, base_url: str = BASE_URL, delay_seconds: float = 1.0):
        self.client = PoliteSession(base_url, USER_AGENT, delay_seconds)
        self.testimonials: List[Testimonial] = []
        self.partners: List[PartnerInstitution] = []
        self.stats: List[SiteStat] = []
        self.nav_links: List[NavLink] = []

    def crawl(self, pages: List[str]) -> None:
        for page in pages:
            log.info("Fetching %s", page)
            soup = self.client.get(page)
            if soup is None:
                log.warning("Skipping extraction for %s (fetch failed)", page)
                continue

            self.testimonials.extend(extract_testimonials(soup, page))
            self.partners.extend(extract_partner_institutions(soup, page))
            self.stats.extend(extract_stats(soup, page))
            self.nav_links.extend(extract_nav_links(soup, page))

        self._deduplicate()

    def _deduplicate(self) -> None:
        self.testimonials = list({t.name + t.quote: t for t in self.testimonials}.values())
        self.partners = list({p.name: p for p in self.partners}.values())
        self.nav_links = list({(n.section, n.text, n.url): n for n in self.nav_links}.values())

    @property
    def total_records(self) -> int:
        return len(self.testimonials) + len(self.partners) + len(self.stats) + len(self.nav_links)

    def to_excel(self, output_path: str) -> None:
        sheets = {
            "Testimonials": pd.DataFrame([asdict(t) for t in self.testimonials]),
            "Partner Institutions": pd.DataFrame([asdict(p) for p in self.partners]),
            "Site Stats": pd.DataFrame([asdict(s) for s in self.stats]),
            "Navigation Links": pd.DataFrame([asdict(n) for n in self.nav_links]),
        }
        summary = pd.DataFrame([
            {"Sheet": name, "Rows": len(df)} for name, df in sheets.items()
        ] + [{"Sheet": "TOTAL", "Rows": self.total_records}])

        try:
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                summary.to_excel(writer, sheet_name="Summary", index=False)
                for name, df in sheets.items():
                    if df.empty:
                        df = pd.DataFrame([{"note": "No records extracted for this page set"}])
                    df.to_excel(writer, sheet_name=name[:31], index=False)
                self._autofit_columns(writer)
        except Exception as exc:
            log.error("Failed to write Excel output: %s", exc)
            raise

        log.info("Wrote %d total records across %d sheets to %s",
                  self.total_records, len(sheets) + 1, output_path)

    @staticmethod
    def _autofit_columns(writer: "pd.ExcelWriter") -> None:
        for sheet in writer.sheets.values():
            for column_cells in sheet.columns:
                length = max((len(str(cell.value)) for cell in column_cells if cell.value), default=10)
                sheet.column_dimensions[column_cells[0].column_letter].width = min(length + 2, 60)



# CLI entry point

def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape ShadowFox's public site into an Excel workbook.")
    parser.add_argument("--url", default=BASE_URL, help="Base URL to scrape")
    parser.add_argument("--pages", nargs="+", default=DEFAULT_PAGES,
                         help="Paths to crawl, e.g. / /approach /domains /merch")
    parser.add_argument("--output", default="shadowfox_scraped_data.xlsx", help="Output .xlsx path")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds to wait between requests")
    args = parser.parse_args()

    log.info("Starting ShadowFox scrape — base=%s pages=%s", args.url, args.pages)
    scraper = ShadowFoxScraper(base_url=args.url, delay_seconds=args.delay)
    scraper.crawl(args.pages)

    if scraper.total_records == 0:
        log.error("No records extracted at all — site structure may have changed. "
                   "Check shadowfox_scraper.log for details.")
        sys.exit(1)

    scraper.to_excel(args.output)
    log.info("Done. %d total records written to %s", scraper.total_records, args.output)


if __name__ == "__main__":
    main()