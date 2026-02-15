#!/usr/bin/env python3
"""
collect_plate_formats.py

Fetches Wikipedia articles for each European country's vehicle registration
plates, then uses the Claude API to extract structured format information
from the wikitext.

Output:
    dataset/metadata/plate_formats.json

Usage:
    python scripts/collect_plate_formats.py              # Full run
    python scripts/collect_plate_formats.py --country DE  # Single country
    python scripts/collect_plate_formats.py --dry-run     # Fetch wikitext only, no LLM calls
"""

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import openai
import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "PlateSpotter/1.0 (https://github.com/platespotter; contact@platespotter.dev)"
REQUEST_DELAY = 1.0

# Countries clickable on the SVG map (ISO code -> country name, Wikipedia article suffix)
COUNTRIES = {
    "AL": ("Albania", "Albania"),
    "AD": ("Andorra", "Andorra"),
    "AM": ("Armenia", "Armenia"),
    "AT": ("Austria", "Austria"),
    "BY": ("Belarus", "Belarus"),
    "BE": ("Belgium", "Belgium"),
    "BA": ("Bosnia and Herzegovina", "Bosnia_and_Herzegovina"),
    "BG": ("Bulgaria", "Bulgaria"),
    "CH": ("Switzerland", "Switzerland"),
    "CY": ("Cyprus", "Cyprus"),
    "CZ": ("Czech Republic", "the_Czech_Republic"),
    "DE": ("Germany", "Germany"),
    "DK": ("Denmark", "Denmark"),
    "EE": ("Estonia", "Estonia"),
    "ES": ("Spain", "Spain"),
    "FI": ("Finland", "Finland"),
    "FR": ("France", "France"),
    "GB": ("United Kingdom", "the_United_Kingdom"),
    "GE": ("Georgia", "Georgia_(country)"),
    "GR": ("Greece", "Greece"),
    "HR": ("Croatia", "Croatia"),
    "HU": ("Hungary", "Hungary"),
    "IE": ("Ireland", "the_Republic_of_Ireland"),
    "IS": ("Iceland", "Iceland"),
    "IT": ("Italy", "Italy"),
    "LI": ("Liechtenstein", "Liechtenstein"),
    "LT": ("Lithuania", "Lithuania"),
    "LU": ("Luxembourg", "Luxembourg"),
    "LV": ("Latvia", "Latvia"),
    "MD": ("Moldova", "Moldova"),
    "ME": ("Montenegro", "Montenegro"),
    "MK": ("North Macedonia", "North_Macedonia"),
    "NL": ("Netherlands", "the_Netherlands"),
    "NO": ("Norway", "Norway"),
    "PL": ("Poland", "Poland"),
    "PT": ("Portugal", "Portugal"),
    "RO": ("Romania", "Romania"),
    "RS": ("Serbia", "Serbia"),
    "SE": ("Sweden", "Sweden"),
    "SI": ("Slovenia", "Slovenia"),
    "SK": ("Slovakia", "Slovakia"),
    "TR": ("Turkey", "Turkey"),
    "UA": ("Ukraine", "Ukraine"),
    "XK": ("Kosovo", "Kosovo"),
}

EXTRACTION_PROMPT = """\
You are given the raw wikitext of a Wikipedia article about vehicle registration plates of {country_name}.

Extract the following information about the CURRENT STANDARD private vehicle registration plate. If a piece of information is not available in the article, use null for that field.

Return ONLY a JSON object (no markdown, no explanation) with these fields:

{{
  "format_pattern": "The character pattern using L for letter and N for number, e.g. 'LL-NNNN-LL' or 'LLL NNNN'. Show separators (hyphens, spaces) as they appear on the plate.",
  "format_explanation": "Brief explanation of what each part represents (e.g. region code, serial number, etc.)",
  "alphabet": "What alphabet/character set is used (e.g. Latin, Cyrillic, Greek) and any notable restrictions on which letters are used",
  "forbidden_combinations": "Any letter/number combinations that are banned or restricted, and why. null if none mentioned.",
  "vanity_plates": "Whether personalized/vanity plates are available, and any rules or costs. null if not mentioned.",
  "year_introduced": "Year the current plate design/system was introduced",
  "dimensions": "Physical plate dimensions (e.g. '520 × 110 mm')",
  "colors_background": "Background color of the plate",
  "colors_lettering": "Color of the letters/numbers",
  "colors_strip": "Color/description of the side strip or band (e.g. 'Blue EU band with yellow stars'). null if no strip.",
  "typeface": "Name of the font/typeface used on the plate. null if not mentioned.",
  "strip_contents": "What is displayed on the strip/band (e.g. 'EU flag and country code D'). null if no strip."
}}

Here is the wikitext:

{wikitext}
"""


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def fetch_article_wikitext(session: requests.Session, article_suffix: str) -> Optional[str]:
    """Fetch wikitext for a 'Vehicle registration plates of X' article."""
    title = f"Vehicle_registration_plates_of_{article_suffix}"
    time.sleep(REQUEST_DELAY)
    params = {
        "action": "parse",
        "page": title,
        "prop": "wikitext",
        "format": "json",
    }
    resp = session.get(WIKIPEDIA_API_URL, params=params)
    if resp.status_code == 429:
        wait = int(resp.headers.get("Retry-After", 60))
        print(f"  Rate-limited -- waiting {wait}s")
        time.sleep(wait)
        resp = session.get(WIKIPEDIA_API_URL, params=params)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        return None
    return data.get("parse", {}).get("wikitext", {}).get("*")


def extract_with_openai(client: openai.OpenAI, country_name: str, wikitext: str) -> Optional[dict]:
    """Send wikitext to OpenAI and extract structured plate format data."""
    # Truncate very long articles to stay within context limits
    max_chars = 80000
    if len(wikitext) > max_chars:
        wikitext = wikitext[:max_chars] + "\n\n[... article truncated ...]"

    prompt = EXTRACTION_PROMPT.format(
        country_name=country_name,
        wikitext=wikitext,
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

    return json.loads(response_text)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Collect license plate format info from Wikipedia via Claude")
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch wikitext only, skip LLM extraction")
    parser.add_argument("--country", type=str,
                        help="Process only one country (ISO code, e.g. DE)")
    parser.add_argument("--output-dir", type=str, default="dataset",
                        help="Output directory (default: dataset)")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key and not args.dry_run:
        print("Error: OPENAI_API_KEY environment variable is required")
        print("Set it with: export OPENAI_API_KEY=sk-...")
        return

    output_dir = Path(args.output_dir)
    (output_dir / "metadata").mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    client = None
    if not args.dry_run:
        client = openai.OpenAI(api_key=api_key)

    # Determine which countries to process
    countries = dict(COUNTRIES)
    if args.country:
        code = args.country.upper()
        if code not in countries:
            print(f"Unknown country code: {code}")
            print("Available codes:")
            for c, (name, _) in sorted(countries.items()):
                print(f"  {c:4s}  {name}")
            return
        countries = {code: countries[code]}

    # Load existing results for incremental updates
    output_path = output_dir / "metadata" / "plate_formats.json"
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Wikipedia (per-country vehicle registration plate articles)",
        "extraction_model": "gpt-4o-mini",
        "entries": {},
    }
    if output_path.exists() and not args.country:
        with open(output_path) as f:
            existing = json.load(f)
            metadata["entries"] = existing.get("entries", {})

    success = 0
    failed = 0
    skipped = 0

    for iso, (country_name, article_suffix) in countries.items():
        # Skip if already collected (unless single-country mode)
        if iso in metadata["entries"] and not args.country:
            print(f"[{iso}] {country_name} -- already collected, skipping")
            skipped += 1
            continue

        print(f"\n[{iso}] {country_name}")

        # 1. Fetch wikitext
        print(f"  Fetching: Vehicle_registration_plates_of_{article_suffix}")
        wikitext = fetch_article_wikitext(session, article_suffix)

        if wikitext is None:
            print(f"  Article not found!")
            failed += 1
            continue

        print(f"  Wikitext: {len(wikitext)} chars")

        if args.dry_run:
            success += 1
            continue

        # 2. Extract with OpenAI
        print(f"  Extracting format data with OpenAI...")
        try:
            result = extract_with_openai(client, country_name, wikitext)
            if result:
                result["country_name"] = country_name
                result["iso"] = iso
                result["wikipedia_article"] = f"Vehicle_registration_plates_of_{article_suffix}"
                result["extracted_at"] = datetime.now(timezone.utc).isoformat()
                metadata["entries"][iso] = result
                print(f"  Format: {result.get('format_pattern', 'N/A')}")
                success += 1

                # Write incrementally
                metadata["generated_at"] = datetime.now(timezone.utc).isoformat()
                with open(output_path, "w") as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
            else:
                print(f"  No result from OpenAI")
                failed += 1
        except json.JSONDecodeError as e:
            print(f"  Failed to parse OpenAI response: {e}")
            failed += 1
        except openai.APIError as e:
            print(f"  OpenAI API error: {e}")
            failed += 1

    # Final write
    if not args.dry_run:
        metadata["generated_at"] = datetime.now(timezone.utc).isoformat()
        with open(output_path, "w") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\nDone: {success} succeeded, {failed} failed, {skipped} skipped")
    if not args.dry_run:
        print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
