import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "count": 30,
    "api": "https://hacker-news.firebaseio.com/v0",
    "cats": [
        "Software Engineering",
        "AI & Machine Learning",
        "Cybersecurity",
        "Hardware & Electronics",
        "Business & Startups",
        "Finance & Crypto",
        "Health & Med",
        "Science & Space",
        "Politics & Law",
        "Climate & Energy",
        "Art & Design",
        "Productivity",
        "Gaming",
        "Math & Logic"
    ]
}

# --- Jina Reader configuration ---
# Used for high-quality article extraction from arbitrary URLs.
# API key is optional; without it the endpoint still works but rate-limited.
JINA_CFG = {
    "base_url": os.getenv("JINA_API_BASE", "https://r.jina.ai"),
    "api_key": os.getenv("JINA_API_KEY", ""),
    "return_format": os.getenv("JINA_RETURN_FORMAT", "text"),
    "timeout": int(os.getenv("JINA_TIMEOUT", "30")),
}

# --- Extraction tunables  ---
EXTRACT_CFG = {
    "request_timeout": int(os.getenv("EXTRACT_TIMEOUT", "10")),   # HN API timeout (s)
    "scrape_timeout": int(os.getenv("SCRAPE_TIMEOUT", "15")),     # fallback scrape timeout (s)
    "max_words": int(os.getenv("EXTRACT_MAX_WORDS", "400")),      # max words kept per article
    "user_agent": os.getenv("USER_AGENT", "Mozilla/5.0"),
    "sleep_between": float(os.getenv("EXTRACT_SLEEP", "0.05")),   # polite delay between HN calls
}

LLM_CFG = {
    #  gpt-oss-120b
    "model": "openai/gpt-oss-120b",
    "tokens": 1500,
    "temp": 0.0,
    "max_text_chars": int(os.getenv("LLM_MAX_TEXT_CHARS", "3000")),  # truncation for prompt
    "url": os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1"),
    "key": os.getenv("GROQ_API_KEY", "")
}
