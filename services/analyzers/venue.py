from __future__ import annotations
from typing import Dict, Any, List
import json

def venue_sensitivity_matrix(json_path: str) -> Dict[str, Any]:
    """
    Input format: {
      "venue": "...",
      "themes": [{"theme":"...", "salience":1-5, "notes":"..."}],
      "volatility_zones": [{"theme":"...", "trigger":"...", "observed":"..."}]
    }
    """
    data = json.loads(open(json_path, "r", encoding="utf-8").read())
    themes = sorted(data.get("themes", []), key=lambda x: (-x.get("salience",0), x.get("theme","")))
    return {
        "venue": data.get("venue",""),
        "themes": themes,
        "volatility_zones": data.get("volatility_zones", [])
    }
