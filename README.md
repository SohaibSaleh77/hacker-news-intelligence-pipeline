# Hacker News Data Pipeline

This project is an automated ETL data pipeline. It fetches top stories from the Hacker News API, extracts and cleans the article content from their URLs, and leverages an LLM to accurately categorize the articles into predefined topics and extract rich metadata (like summaries, mentioned companies, and key people). It then saves this structured data to a database and generates visual reports.

## Article Extraction with Jina Reader

This pipeline uses the **Jina Reader API** (`https://r.jina.ai/<url>`) to extract clean, main-body text from article URLs. Jina Reader handles JavaScript-rendered content, paywall blockers, ad clutter, and boilerplate removal far more reliably than naive HTML scraping.

### Configuration
- Set `JINA_API_KEY` in `.env` (get a free key at https://jina.ai/).
- If `JINA_API_KEY` is empty/missing, the pipeline still works against the Jina Reader endpoint, but with the public free-tier rate limits.
- Other knobs: `JINA_API_BASE`, `JINA_RETURN_FORMAT` (`text` or `markdown`), `JINA_TIMEOUT`.
- If Jina Reader fails for a given URL, a small BeautifulSoup fallback kicks in so the pipeline stays reliable.
