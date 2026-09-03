import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from src.utils import get_log

log = get_log("Load")

def save(df, fmt, path="outputs/data"):
    if df.empty: return
    if fmt == "csv":
        df.to_csv(f"{path}.csv", index=False)
        log.info(f"Saved {len(df)} to CSV")
    elif fmt == "json":
        df.to_json(f"{path}.json", orient="records", indent=4)
        log.info(f"Saved {len(df)} to JSON")
    elif fmt == "sqlite":
        try:
            d = df.copy()
            d['dt'] = d['dt'].astype(str)
            d = d.drop_duplicates(subset=['id'])

            conn = sqlite3.connect(f"{path}.db")
            cur = conn.cursor()

            cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='news'")
            if cur.fetchone()[0] == 1:
                d.to_sql("tmp", conn, if_exists='replace', index=False)
                cur.execute("DELETE FROM news WHERE id IN (SELECT id FROM tmp)")
                cur.execute("INSERT INTO news SELECT * FROM tmp")
                conn.commit()
                cur.execute("DROP TABLE tmp")
                log.info(f"Upserted {len(df)} to SQLite")
            else:
                d.to_sql("news", conn, if_exists='replace', index=False)
                log.info(f"Loaded {len(df)} to SQLite")
            conn.close()
        except Exception as e:
            log.error(f"DB Error: {e}")

def plot(df, path="outputs/chart.png"):
    if df.empty or 'cat1' not in df.columns: return
    try:
        c = df['cat1'].value_counts()
        plt.figure(figsize=(8, 5))
        c.plot(kind='bar', color='blue')
        plt.title('Topics')
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        log.info(f"Saved chart to {path}")
    except Exception as e:
        log.error(f"Plot Error: {e}")

def report(df):
    if df.empty: return
    log.info("--- REPORT ---")
    log.info(f"Count: {len(df)}")
    log.info(f"Avg words: {df['words'].mean():.1f}")
    log.info("Top Topics:")
    for ln in df['cat1'].value_counts().to_string().split('\n'):
        log.info(ln)
    log.info("--------------")
