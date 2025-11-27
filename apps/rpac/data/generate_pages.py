"""Generate challenge-data.json from authoritative Excel source.

Uses authoritative Excel source (challenge.xlsx) to generate JSON data file
that replaces hardcoded JavaScript data and Python-generated HTML pages.

Output:
    - challenge-data.json (10 employee records)
"""

import json
import sys
from pathlib import Path

# Add packages to path
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent.parent / "src")
)

from cpmf_rpachallenge import from_xlsx, load_records

# Configuration
OUTPUT_DIR = Path(__file__).parent
EXCEL_PATH = Path(__file__).parent.parent / "assets" / "challenge.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "challenge-data.json"


def generate_json_data() -> dict:
    """Generate JSON data structure from Excel.

    Returns:
        Dictionary with version and records array
    """
    print("=" * 60)
    print("Challenge Data JSON Generator")
    print("=" * 60)

    # Load data from Excel (authoritative source)
    print(f"\n[1/3] Loading data from {EXCEL_PATH.name}...")
    source = from_xlsx(str(EXCEL_PATH))
    all_records = load_records(source)[:10]  # First 10 records
    print(f"[OK] Loaded {len(all_records)} records")

    # Convert to JSON structure
    print(f"\n[2/3] Converting to JSON format...")
    json_data = {
        "version": "1.0",
        "records": [
            {
                "first_name": record.first_name,
                "last_name": record.last_name,
                "company_name": record.company_name,
                "role": record.role,
                "address": record.address,
                "email": record.email,
                "phone": record.phone,
            }
            for record in all_records
        ]
    }
    print(f"[OK] Converted {len(json_data['records'])} records")

    return json_data


def main():
    """Generate challenge-data.json file."""
    # Generate data
    json_data = generate_json_data()

    # Write JSON file
    print(f"\n[3/3] Writing JSON file...")
    OUTPUT_FILE.write_text(
        json.dumps(json_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"[OK] Generated {OUTPUT_FILE.name}")

    # Verification
    print(f"\n[VERIFY] File size: {OUTPUT_FILE.stat().st_size} bytes")
    print(f"[VERIFY] Records: {len(json_data['records'])}")
    print(f"[VERIFY] Sample record keys: {list(json_data['records'][0].keys())}")

    print("\n" + "=" * 60)
    print("Generation complete!")
    print(f"Output: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
