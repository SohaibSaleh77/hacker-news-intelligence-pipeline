import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.utils import get_log, timer, get_domain
from src.llm import init_ai, parse

log = get_log("Transform")

@timer
def add_feats(df):
    log.info("Adding feats...")
    if df.empty: return df
    df['domain'] = df['url'].apply(get_domain)
    df['words'] = df['text'].apply(lambda x: len(str(x).split()))
    df['dt'] = pd.to_datetime(df['time'], unit='s')
    return df

@timer
def transform(df, cats, workers=1):
    log.info(f"AI parsing with {workers} workers...")
    if df.empty: return df

    ai = init_ai()
    res = [None] * len(df)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(parse, ai, r['text'], cats): i for i, r in df.iterrows()}
        for f in tqdm(as_completed(futs), total=len(futs), desc="AI Tasks"):
            res[futs[f]] = f.result()

    c1, c2, c3 = [], [], []
    s1, s2, s3 = [], [], []
    sums, orgs, tech, ppl = [], [], [], []

    for r in res:
        if r:
            tc = r.top_cats
            c1.append(tc[0].name if len(tc)>0 else "Unknown")
            s1.append(tc[0].score if len(tc)>0 else 0.0)
            c2.append(tc[1].name if len(tc)>1 else None)
            s2.append(tc[1].score if len(tc)>1 else 0.0)
            c3.append(tc[2].name if len(tc)>2 else None)
            s3.append(tc[2].score if len(tc)>2 else 0.0)
            sums.append(r.summary)
            orgs.append(", ".join(r.orgs))
            tech.append(", ".join(r.tech))
            ppl.append(", ".join(r.people))
        else:
            c1.append("Error"); s1.append(0.0)
            c2.append(None); s2.append(0.0)
            c3.append(None); s3.append(0.0)
            sums.append(None); orgs.append(None)
            tech.append(None); ppl.append(None)

    df['cat1'] = c1
    df['score1'] = s1
    df['cat2'] = c2
    df['score2'] = s2
    df['cat3'] = c3
    df['score3'] = s3
    df['summary'] = sums
    df['orgs'] = orgs
    df['tech'] = tech
    df['people'] = ppl

    return df
