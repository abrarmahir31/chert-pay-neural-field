#!/usr/bin/env python
"""Look up reference candidates on Crossref (prints compact records for manual confirmation).

Usage: python scripts/check_references.py "free text query" ["another query" ...]
       python scripts/check_references.py --doi 10.xxxx/yyyy [...]
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.crossref.org/works"
SEL = "DOI,title,author,container-title,issued,volume,issue,page,type"


def get(url, tries=5):
    req = urllib.request.Request(url, headers={"User-Agent": "reference-checker"})
    for i in range(tries):
        try:
            time.sleep(2.0)  # stay well under the public rate limit
            return json.load(urllib.request.urlopen(req, timeout=40))["message"]
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == tries - 1:
                raise
            time.sleep(10 * (i + 1))


def show(it):
    au = "; ".join(f"{a.get('family', '')}, {a.get('given', '')}" for a in it.get("author", [])[:7])
    print(" |", it.get("DOI"), "|", (it.get("title") or [""])[0][:110], "|", au, "|",
          (it.get("container-title") or [""])[0], "|", it.get("issued", {}).get("date-parts"),
          it.get("volume"), it.get("issue"), it.get("page"), it.get("type"))


def main():
    args = sys.argv[1:]
    if args and args[0] == "--doi":
        for d in args[1:]:
            try:
                show(get(f"{API}/{urllib.parse.quote(d)}"))
            except Exception as e:  # noqa: BLE001
                print(" | NOT FOUND", d, e)
        return
    for q in args:
        print(q[:60])
        url = f"{API}?rows=2&select={SEL}&query.bibliographic={urllib.parse.quote(q)}"
        for it in get(url)["items"]:
            show(it)


if __name__ == "__main__":
    main()
