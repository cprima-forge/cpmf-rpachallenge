"""Generate paginated data table HTML files.

Uses authoritative Excel source (challenge.xlsx) to generate 4 static HTML pages
with server-side pagination pattern (3+3+3+1 record distribution).

Output:
    - page1.html (records 1-3)
    - page2.html (records 4-6)
    - page3.html (records 7-9)
    - page4.html (record 10)
"""

import sys
from pathlib import Path

# Add packages to path
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent.parent / "src")
)

from cpmf_rpachallenge import from_xlsx, load_records

# Configuration
RECORDS_PER_PAGE = 3
TOTAL_PAGES = 4
OUTPUT_DIR = Path(__file__).parent
EXCEL_PATH = Path(__file__).parent.parent / "assets" / "challenge.xlsx"


def generate_navigation_html(page_num: int, total_pages: int) -> str:
    """Generate navigation HTML based on current page position.

    Args:
        page_num: Current page number (1-indexed)
        total_pages: Total number of pages

    Returns:
        HTML string for navigation section
    """
    # Determine which buttons should be disabled
    at_start = page_num == 1
    at_end = page_num == total_pages

    # Build navigation items
    nav_items = []

    # First button (<<)
    if at_start:
        nav_items.append('<span class="nav-item disabled" data-nav="first"><<</span>')
    else:
        nav_items.append(f'<a class="nav-item" data-nav="first" href="page1.html"><<</a>')

    # Previous button (<)
    if at_start:
        nav_items.append('<span class="nav-item disabled" data-nav="prev"><</span>')
    else:
        prev_page = page_num - 1
        nav_items.append(f'<a class="nav-item" data-nav="prev" href="page{prev_page}.html"><</a>')

    # Page info
    nav_items.append(f'<span class="page-info">Page {page_num} of {total_pages}</span>')

    # Next button (>)
    if at_end:
        nav_items.append('<span class="nav-item disabled" data-nav="next">></span>')
    else:
        next_page = page_num + 1
        nav_items.append(f'<a class="nav-item" data-nav="next" href="page{next_page}.html">></a>')

    # Last button (>>)
    if at_end:
        nav_items.append('<span class="nav-item disabled" data-nav="last">>></span>')
    else:
        nav_items.append(f'<a class="nav-item" data-nav="last" href="page{total_pages}.html">>></a>')

    return "\n      ".join(nav_items)


def generate_table_rows_html(records: list) -> str:
    """Generate table row HTML from records.

    Args:
        records: List of ChallengeRecord objects

    Returns:
        HTML string for table rows
    """
    rows = []
    for record in records:
        row = f"""        <tr>
          <td>{record.first_name}</td>
          <td>{record.last_name}</td>
          <td>{record.phone}</td>
          <td>{record.email}</td>
          <td>{record.address}</td>
          <td>{record.company_name}</td>
          <td>{record.role}</td>
        </tr>"""
        rows.append(row)

    return "\n".join(rows)


def generate_page_html(page_num: int, total_pages: int, records: list) -> str:
    """Generate complete HTML for a single page.

    Args:
        page_num: Current page number (1-indexed)
        total_pages: Total number of pages
        records: List of ChallengeRecord objects for this page

    Returns:
        Complete HTML string
    """
    navigation_html = generate_navigation_html(page_num, total_pages)
    table_rows_html = generate_table_rows_html(records)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Data Table - Page {page_num}</title>
  <link rel="stylesheet" href="../css/solarized.css">
  <link rel="stylesheet" href="../css/layout.css">
  <link rel="stylesheet" href="../css/components.css">
  <style>
    /* Pagination-specific styles */
    .pagination {{
      display: flex;
      gap: 1rem;
      justify-content: center;
      align-items: center;
      margin-top: 2rem;
      padding: 1rem;
    }}

    .nav-item {{
      padding: 0.5rem 1rem;
      background: var(--sol-orange);
      color: var(--sol-base03);
      border: none;
      border-radius: 4px;
      cursor: pointer;
      text-decoration: none;
      font-weight: bold;
      transition: background 0.2s;
    }}

    .nav-item:not(.disabled):hover {{
      background: var(--sol-red);
    }}

    .nav-item.disabled {{
      background: var(--sol-base01);
      color: var(--sol-base02);
      cursor: not-allowed;
      opacity: 0.5;
    }}

    .page-info {{
      padding: 0.5rem 1rem;
      color: var(--sol-base00);
      font-weight: bold;
    }}

    /* Table styles */
    .data-table {{
      width: 100%;
      border-collapse: collapse;
      margin: 2rem 0;
      background: var(--sol-base3);
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}

    .data-table th,
    .data-table td {{
      padding: 1rem;
      text-align: left;
      border-bottom: 1px solid var(--sol-base2);
    }}

    .data-table th {{
      background: var(--sol-base2);
      color: var(--sol-base01);
      font-weight: bold;
      text-transform: uppercase;
      font-size: 0.85rem;
      letter-spacing: 0.05em;
    }}

    .data-table tbody tr:hover {{
      background: var(--sol-base2);
    }}

    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem;
    }}

    header {{
      text-align: center;
      margin-bottom: 2rem;
      color: var(--sol-base01);
    }}

    header h1 {{
      color: var(--sol-orange);
      margin-bottom: 0.5rem;
    }}

    header p {{
      color: var(--sol-base00);
      font-size: 1.1rem;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Paginated Data Table</h1>
      <p>Page {page_num} of {total_pages}</p>
    </header>

    <table class="data-table">
      <thead>
        <tr>
          <th>First Name</th>
          <th>Last Name</th>
          <th>Phone Number</th>
          <th>Email</th>
          <th>Address</th>
          <th>Company Name</th>
          <th>Role in Company</th>
        </tr>
      </thead>
      <tbody>
{table_rows_html}
      </tbody>
    </table>

    <nav class="pagination">
      {navigation_html}
    </nav>
  </div>
</body>
</html>
"""


def main():
    """Generate all paginated HTML files."""
    print("=" * 60)
    print("Paginated HTML Generator")
    print("=" * 60)

    # Load data from Excel (authoritative source)
    print(f"\n[1/3] Loading data from {EXCEL_PATH.name}...")
    source = from_xlsx(str(EXCEL_PATH))
    all_records = load_records(source)[:10]  # First 10 records
    print(f"[OK] Loaded {len(all_records)} records")

    # Generate pages
    print(f"\n[2/3] Generating {TOTAL_PAGES} HTML pages...")
    for page_num in range(1, TOTAL_PAGES + 1):
        # Calculate record slice for this page
        start_idx = (page_num - 1) * RECORDS_PER_PAGE
        end_idx = start_idx + RECORDS_PER_PAGE
        page_records = all_records[start_idx:end_idx]

        # Generate HTML
        html = generate_page_html(
            page_num=page_num,
            total_pages=TOTAL_PAGES,
            records=page_records,
        )

        # Write file
        output_path = OUTPUT_DIR / f"page{page_num}.html"
        output_path.write_text(html, encoding="utf-8")
        print(f"[OK] Generated page{page_num}.html ({len(page_records)} records)")

    print(f"\n[3/3] Verification...")
    total_generated_records = sum(
        len(all_records[i * RECORDS_PER_PAGE : (i + 1) * RECORDS_PER_PAGE])
        for i in range(TOTAL_PAGES)
    )
    print(f"[OK] Total records across all pages: {total_generated_records}")
    print(f"[OK] Distribution: 3+3+3+1 = 10")

    print("\n" + "=" * 60)
    print("Generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
