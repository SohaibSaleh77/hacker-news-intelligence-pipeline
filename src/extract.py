import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
from src.config import EXTRACT_CFG, JINA_CFG
from src.utils import get_log, timer, retry, clean

log = get_log("Extract")

# Counters tracking which extraction method served each article
_stats = {"jina": 0, "fallback": 0, "hn-native": 0}

@retry(retries=3, delay=1)
def get_ids(api):
    log.info("Getting IDs...")
    r = requests.get(f"{api}/topstories.json", timeout=EXTRACT_CFG["request_timeout"])
    r.raise_for_status()
    return r.json()

@retry(retries=2, delay=1)
def get_story(api, sid):
    r = requests.get(f"{api}/item/{sid}.json", timeout=EXTRACT_CFG["request_timeout"])
    r.raise_for_status()
    return r.json()

def jina_reader(url):
    """
    Fetch clean article text via the Jina Reader API.
    - If JINA_API_KEY is set, it is sent as a Bearer token for higher rate limits.
    - If the key is missing, the endpoint still works at free-tier limits.
    - Returns an empty string on any failure so callers can fall back.
    """
    if not url:
        return ""
    try:
        headers = {
            "User-Agent": EXTRACT_CFG["user_agent"],
            "X-Return-Format": JINA_CFG["return_format"],
            "X-Timeout": str(JINA_CFG["timeout"]),
        }
        if JINA_CFG["api_key"]:
            headers["Authorization"] = f"Bearer {JINA_CFG['api_key']}"

        endpoint = f"{JINA_CFG['base_url']}/{url}"
        # Allow a small buffer beyond the configured server-side timeout
        r = requests.get(endpoint, headers=headers, timeout=JINA_CFG["timeout"] + 5)
        r.raise_for_status()
        return r.text.strip()
    except Exception as e:
        log.warning(f"Jina Reader failed for {url}: {e}")
        return ""

@retry(retries=1, delay=1)
def get_text(url):
    """
    Extract article text. Returns (text, method_used).
    Primary: Jina Reader API (clean, JS-aware, boilerplate-stripped).
    Fallback: direct fetch + simple <p> tag parsing with BeautifulSoup.
    """
    if not url:
        return "", "none"

    # --- Primary: Jina Reader ---
    text = jina_reader(url)
    if text:
        return " ".join(text.split()[:EXTRACT_CFG["max_words"]]), "jina"

    # --- Fallback: naive scrape ---
    try:
        h = {"User-Agent": EXTRACT_CFG["user_agent"]}
        r = requests.get(url, headers=h, timeout=EXTRACT_CFG["scrape_timeout"])
        soup = BeautifulSoup(r.content, 'html.parser')
        p = soup.find_all('p')
        t = " ".join([x.get_text() for x in p])
        return " ".join(t.split()[:EXTRACT_CFG["max_words"]]), "fallback"
    except Exception:
        return "", "fallback"

@timer
def extract(api, count):
    # Reset per-run counters
    _stats.update({"jina": 0, "fallback": 0, "hn-native": 0})

    ids = get_ids(api)
    if not ids: return pd.DataFrame()

    recs = []
    log.info(f"Downloading {count} stories...")

    for sid in ids[:count]:
        d = get_story(api, sid)
        if d and d.get("type") == "story" and "title" in d:
            txt = d.get("text", "")
            method = "hn-native"   # HN text posts already contain body text

            if not txt and d.get("url"):
                txt, method = get_text(d.get("url"))

            # Log which extractor served this article
            log.info(f"  [{method}] {d.get('url', '<no-url>')}")
            _stats[method] = _stats.get(method, 0) + 1

            title = d.get("title", "")
            full = f"{title}. {txt}"

            recs.append({
                "id": d.get("id"),
                "title": title,
                "url": d.get("url", ""),
                "text": clean(full),
                "score": d.get("score", 0),
                "by": d.get("by", "Unknown"),
                "time": d.get("time", 0)
            })
        time.sleep(EXTRACT_CFG["sleep_between"])

    # Summary log: how many articles each method served
    log.info("Extraction summary: " + ", ".join(f"{k}={v}" for k, v in _stats.items()))
    return pd.DataFrame(recs)
