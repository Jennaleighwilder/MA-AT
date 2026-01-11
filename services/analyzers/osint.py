from __future__ import annotations
from typing import Dict, Any, List, Tuple
import json

def summarize_public_social(json_path: str) -> Dict[str, Any]:
    """
    Input format: list of items with {platform, url, public_text, tags(optional)}
    Output: topic exposure summary + declared positions ledger (verbatim snippets)
    """
    data = json.loads(open(json_path, "r", encoding="utf-8").read())
    topics = {}
    snippets = []
    for item in data:
        text = (item.get("public_text") or "").strip()
        for t in item.get("tags") or []:
            topics[t] = topics.get(t, 0) + 1
        if text:
            snippets.append({
                "platform": item.get("platform",""),
                "url": item.get("url",""),
                "snippet": text[:280]
            })
    return {
        "topic_exposure_counts": dict(sorted(topics.items(), key=lambda x: (-x[1], x[0]))),
        "declared_positions_ledger": snippets
    }
