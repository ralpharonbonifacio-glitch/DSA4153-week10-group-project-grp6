"""
Validation and duplicate / conflict detection (Member 3).

All functions work on pandas DataFrames that use the canonical columns:
country, continent, year, lifeExp, pop, gdpPercap
"""

from collections import Counter

import numpy as np
import pandas as pd

CANONICAL_COLUMNS = ["country", "continent", "year", "lifeExp", "pop", "gdpPercap"]
KEY_COLUMNS = ["country", "year"]
TEXT_COLUMNS = ["country", "continent"]
NUMERIC_COLUMNS = ["year", "lifeExp", "pop", "gdpPercap"]
INTEGER_COLUMNS = ["year", "pop"]

# Fallback rules used when manifest.json does not provide "validation_rules".
# Keep these in sync with data/manifest.json.
DEFAULT_RULES = {
    "allowed_continents": ["Africa", "Americas", "Asia", "Europe", "Oceania"],
    "year": {"min": 1800, "max": 2100},
    "lifeExp": {"min": 0, "max": 125},
    "pop": {"min": 0},
    "gdpPercap": {"min": 0},
}


def load_rules(manifest=None):
    """Build the validation rules from a manifest dict (or use the defaults).

    The manifest may contain a "validation_rules" section that uses the same
    structure as DEFAULT_RULES. Missing parts fall back to the defaults.
    """
    rules = {key: (dict(value) if isinstance(value, dict) else list(value))
             for key, value in DEFAULT_RULES.items()}
    manifest_rules = (manifest or {}).get("validation_rules", {})
    for key, value in manifest_rules.items():
        if isinstance(value, dict) and isinstance(rules.get(key), dict):
            rules[key].update(value)
        else:
            rules[key] = value
    return rules