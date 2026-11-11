#!/usr/bin/env python
"""Download all raw data into data/raw/ (never committed).

Sources
-------
1. Kansas Geological Survey (KGS) bulk archives (primary, authoritative):
   ks_las_files (LAS index), ks_wells (headers, elevations), ks_tops (formation tops).
2. Original LAS files for Barber County (API prefix 15-007), one request per file,
   from the URLs listed in the KGS LAS index.
3. (optional, --kaggle) the Kaggle repackaging
   ainiashiqinn/barber-county-well-log-dataset-kansas, used only for the provenance check.
   Public download via kagglehub; if Kaggle asks for credentials they are read from the
   environment variables KAGGLE_USERNAME / KAGGLE_KEY only.

Usage: python scripts/download_data.py [--kaggle] [--limit N]
"""
from __future__ import annotations

import argparse
import csv
import io
import sys
import time
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
KGS_ARCHIVE = "https://www.kgs.ku.edu/PRS/Ora_Archive/{name}.zip"
ARCHIVES = ("ks_las_files", "ks_wells", "ks_tops")
COUNTY_API_PREFIX = "15-007"  # Barber County, Kansas
KAGGLE_SLUG = "ainiashiqinn/barber-county-well-log-dataset-kansas"
UA = {"User-Agent": "chert-pay-neural-field-research-downloader"}


def fetch(url: str, retries: int = 4) -> bytes:
    for i in range(retries + 1):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            if i == retries or getattr(e, "code", None) in (403, 404):
                raise
            print(f"  retry {i + 1} for {url}: {e}", file=sys.stderr)
            time.sleep(2 ** (i + 1))
    raise RuntimeError("unreachable")


def get_archives() -> None:
    for name in ARCHIVES:
        out = RAW / "kgs" / name
        if (out / f"{name}.txt").exists():
            continue
        print(f"downloading {name}.zip")
        out.mkdir(parents=True, exist_ok=True)
        zipfile.ZipFile(io.BytesIO(fetch(KGS_ARCHIVE.format(name=name)))).extractall(out)


def barber_las_rows() -> list[dict]:
    path = RAW / "kgs" / "ks_las_files" / "ks_las_files.txt"
    with open(path, encoding="latin-1", newline="") as f:
        return [r for r in csv.DictReader(f) if (r["API"] or "").startswith(COUNTY_API_PREFIX)]


def live_url(index_url: str) -> str:
    """The KGS index lists a retired path (/b_1/WebDocs/WellLogs/...). The live path is
    /WellLogs/..., which redirects to the KGS file store (kgsimages.blob.core.windows.net)."""
    return index_url.replace("/b_1/WebDocs/WellLogs/", "/WellLogs/")


def get_las(limit: int | None, delay: float, workers: int = 4) -> None:
    out = RAW / "kgs" / "las"
    out.mkdir(parents=True, exist_ok=True)
    rows = barber_las_rows()
    rows = rows[:limit] if limit else rows
    failed = []

    def one(r: dict) -> None:
        url = live_url(r["URL"].strip())
        dest = out / url.rsplit("/", 1)[-1]
        if dest.exists() and dest.stat().st_size > 0:
            return
        try:
            data = fetch(url)
            tmp = dest.with_suffix(".part")
            tmp.write_bytes(data)
            tmp.rename(dest)
        except Exception as e:  # noqa: BLE001
            failed.append((url, str(e)))
        time.sleep(delay)

    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(one, rows))
    (RAW / "kgs" / "las_download_failures.txt").write_text(
        "\n".join(f"{u}\t{e}" for u, e in failed)
    )
    print(f"LAS files requested: {len(rows)}, failed: {len(failed)}")


def get_kaggle() -> None:
    import os

    import kagglehub

    os.environ.setdefault("KAGGLEHUB_CACHE", str(RAW / "kagglehub"))
    print("kaggle copy at", kagglehub.dataset_download(KAGGLE_SLUG))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kaggle", action="store_true", help="also fetch the Kaggle repackaging")
    ap.add_argument("--limit", type=int, default=None, help="only first N LAS files (debug)")
    ap.add_argument("--delay", type=float, default=0.15, help="pause between LAS requests [s]")
    a = ap.parse_args()
    get_archives()
    get_las(a.limit, a.delay)
    if a.kaggle:
        get_kaggle()


if __name__ == "__main__":
    main()
