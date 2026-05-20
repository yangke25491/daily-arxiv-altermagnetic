import requests
import feedparser
import re
from datetime import date, timedelta
import os

SEARCH_KEYWORD = "altermagnetic"

TIME_RANGE_DAYS = 30
CATEGORY1 = "cond-mat.supr-con"
CATEGORY2 = "cond-mat.str-el"
MAX_RESULTS = 100
OUTPUT_FILE = os.environ.get("OUTPUT_FILE", "altermagnetic_recent_papers.md")

def process_latex_math(text):
    result = []
    parts = re.split(r"(\\$[^$]+\\$)", text)
    for part in parts:
        if re.match(r"^\\$[^$]+\\$$b", part):
            inner = part[1:-1]
            if re.match(r"^_[... SHORTENED