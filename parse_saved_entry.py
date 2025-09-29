import sys
import os
import json
from typing import Dict
from bs4 import BeautifulSoup


def parse_entry_html(html: str) -> Dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    result: Dict[str, str] = {}

    # Try tables with th/td
    for row in soup.select("table tr"):
        th = row.find("th")
        if th:
            # value in next td
            td = row.find("td")
            if td:
                k = th.get_text(strip=True)
                v = td.get_text(" ", strip=True)
                if k and v:
                    result[k] = v

    # Try definition lists dt/dd
    for dt in soup.select("dl dt"):
        dd = dt.find_next_sibling("dd")
        if dd:
            k = dt.get_text(strip=True)
            v = dd.get_text(" ", strip=True)
            if k and v and k not in result:
                result[k] = v

    # Fallback: two-column rows (first td label, second value)
    for row in soup.select("table tr"):
        tds = row.find_all("td")
        if len(tds) >= 2:
            k = tds[0].get_text(strip=True)
            v = tds[1].get_text(" ", strip=True)
            if k and v and k not in result:
                result[k] = v

    return result


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python parse_saved_entry.py /path/to/entry_raw.html")
        return 2
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return 2
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    data = parse_entry_html(html)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


