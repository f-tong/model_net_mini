import json
import requests
import pandas as pd

# -----------------------------
# 1. Load all cPAPERS arXiv IDs
# -----------------------------

def load_cpapers_arxiv_ids(paths):
    arxiv_ids = set()
    for path in paths:
        with open(path, "r") as f:
            for line in f:
                obj = json.loads(line)
                pid = obj.get("paper_id", "")
                if pid:
                    # Normalize arXiv IDs by removing version suffix (e.g., v1)
                    arxiv_ids.add(pid.split("v")[0])
    return arxiv_ids

cpapers_paths = [
    "table_train.jsonl",
    "table_dev.jsonl",
    "table_test.jsonl"
]

cpapers_arxiv_ids = load_cpapers_arxiv_ids(cpapers_paths)
print(f"Loaded {len(cpapers_arxiv_ids)} unique cPAPERS arXiv IDs")

# -------------------------------------------------------
# 2. Convert ModelTables corpusIds → arXiv IDs via API
# -------------------------------------------------------

def corpusid_to_arxiv(corpus_id):
    url = f"https://api.semanticscholar.org/graph/v1/paper/{int(corpus_id)}?fields=externalIds"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        ext = data.get("externalIds", {})
        arxiv = ext.get("ArXiv", None)
        if arxiv:
            return arxiv.split("v")[0]  # normalize
        return None
    except Exception:
        return None

# t2i_df is your ModelTables dataframe
# Columns: ['query_title','retrieved_title','paperId','corpusId','paper_identifier','query_status']

modeltables_arxiv_map = {}  # corpusId → arXiv ID

for cid in t2i_df["corpusId"].dropna().unique():
    arxiv = corpusid_to_arxiv(cid)
    if arxiv:
        modeltables_arxiv_map[cid] = arxiv

print(f"Resolved {len(modeltables_arxiv_map)} ModelTables corpusIds to arXiv IDs")

# -------------------------------------------------------
# 3. Compute intersection (arXiv IDs)
# -------------------------------------------------------

modeltables_arxiv_ids = set(modeltables_arxiv_map.values())
intersection_arxiv = modeltables_arxiv_ids.intersection(cpapers_arxiv_ids)

print(f"Intersection size: {len(intersection_arxiv)}")

# -------------------------------------------------------
# 4. Print intersection as Semantic Scholar corpusIds
# -------------------------------------------------------

intersection_corpusIds = [
    cid for cid, ax in modeltables_arxiv_map.items()
    if ax in intersection_arxiv
]

print("CorpusIds that overlap with cPAPERS:")
for cid in intersection_corpusIds:
    print(cid)
