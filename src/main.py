import argparse
import pandas as pd
from src.config import CONFIG
from src.utils import get_log, timer
from src.extract import extract
from src.transform import add_feats, transform
from src.load import save, plot, report

log = get_log("Main")

def get_args():
    p = argparse.ArgumentParser()
    p.add_argument("--count", type=int, default=CONFIG["count"])
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--fmt", choices=["csv", "json", "sqlite"], default="csv")
    return p.parse_args()

@timer
def run(args):
    log.info("START")
    raw = extract(CONFIG["api"], args.count)
    if raw.empty: return

    feats = add_feats(raw)
    final = transform(feats, CONFIG["cats"], args.workers)

    save(final, args.fmt)
    plot(final)
    report(final)

    log.info("END")
    return final

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    args = get_args()
    res = run(args)
    if res is not None:
        log.info("SAMPLE:")
        for _, r in res[['title', 'cat1']].head(2).iterrows():
            log.info(f"[{r['cat1']}] {r['title']}")
