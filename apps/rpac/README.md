# RPA Challenge Clone

Full-featured clone of [rpachallenge.com](https://rpachallenge.com) with Solarized Light theme, designed for automation testing and training.

## Features

- **Form Randomization**: Fields shuffle positions after each submission (Fisher-Yates algorithm)
- **Accurate Timer**: 10ms precision timing using `Date.now()`
- **Score Tracking**: Tracks 70 total fields across 10 rounds
- **Excel Download**: Challenge data available as `challenge.xlsx`
- **Solarized Light Theme**: Professional color scheme with excellent readability
- **Pure Vanilla JavaScript**: No frameworks, fast loading, easy to modify

## Selector Compatibility

All HTML selectors match the original rpachallenge.com for automation testing compatibility with the `cpmf-rpachallenge` Python package.

### Critical Selectors

**Form Fields:**
```javascript
document.querySelector('[ng-reflect-name="labelFirstName"]')
document.querySelector('[ng-reflect-name="labelLastName"]')
document.querySelector('[ng-reflect-name="labelPhone"]')
document.querySelector('[ng-reflect-name="labelEmail"]')
document.querySelector('[ng-reflect-name="labelAddress"]')
document.querySelector('[ng-reflect-name="labelCompanyName"]')
document.querySelector('[ng-reflect-name="labelRole"]')
```

**Buttons:**
```javascript
document.querySelector('.uiColorButton')  // START/RESET button
document.querySelector('input[type="submit"]')  // Submit button
```

**Results:**
```javascript
document.querySelector('.congratulations')  // Results container
document.querySelector('.message1')  // "Congratulations!" text
document.querySelector('.message2')  // Score and time message
```

**Excel Link:**
```javascript
document.querySelector('a[href*="challenge.xlsx"]')
```

## Local Testing

Open `index.html` in any modern browser. No server required.

```bash
# Or use Python's built-in server
cd apps/rpac
python -m http.server 8000
```

Then navigate to `http://localhost:8000`

## GitHub Pages Deployment

This site is designed to be hosted on GitHub Pages from the `/docs` folder.

### Setup Steps:

1. Push the `apps/rpac/` directory to your GitHub repository
2. Go to **Settings** > **Pages**
3. Set **Source** to "GitHub Actions"
4. Create a workflow file (see below)
5. Push to trigger deployment

Your site will be available at:
```
https://<username>.github.io/<repo>/apps/rpac/
```

## Excel Schema

The `challenge.xlsx` file contains 10 records with 7 fields each:

| Column | Description |
|--------|-------------|
| First Name | First name of person |
| Last Name | Last name of person |
| Phone Number | Phone number |
| Email | Email address |
| Address | Street address |
| Company Name | Company name |
| Role in Company | Job title/role |

## File Structure

```
apps/rpac/
├── .nojekyll              # Disables Jekyll processing
├── index.html             # Main page
├── README.md              # This file
├── generate_excel.py      # Script to regenerate Excel file
├── css/
│   ├── solarized.css      # Color variables
│   ├── layout.css         # Grid & responsive design
│   └── components.css     # Buttons, forms, results
├── js/
│   ├── config.js          # Field configuration
│   ├── data.js            # Challenge data (10 records)
│   ├── timer.js           # Timer class
│   ├── scoring.js         # Score tracking
│   ├── form-manager.js    # Form rendering & validation
│   └── app.js             # Main application controller
└── assets/
    └── challenge.xlsx     # Excel file with challenge data
```

## Automation Testing

This clone is fully compatible with the [`cpmf-rpachallenge`](https://github.com/cprima-forge/cpmf-rpachallenge) Python package for Playwright-based automation.

```python
from playwright.sync_api import sync_playwright
from cpmf_rpachallenge import RPAChallengeClient, PlaywrightBackend

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    # Use your GitHub Pages URL or local server
    page.goto("https://<username>.github.io/<repo>/apps/rpac/")

    backend = PlaywrightBackend(page)
    client = RPAChallengeClient(backend=backend)

    result = client.run()
    print(f"Success rate: {result.success_rate}%")

    browser.close()
```

## Regenerating Excel File

If you need to regenerate the Excel file with different data:

1. Edit `js/data.js` with new challenge data
2. Edit `generate_excel.py` to match the new data
3. Run the script:

```bash
uv run --with openpyxl python generate_excel.py
```

## Color Scheme

Based on the Solarized Light palette by Ethan Schoonover:

| Variable | Color | Usage |
|----------|-------|-------|
| `--sol-base03` | #fdf6e3 | Background |
| `--sol-base02` | #eee8d5 | Background highlights |
| `--sol-base01` | #93a1a1 | Comments / secondary |
| `--sol-base00` | #839496 | Body text |
| `--sol-base0` | #657b83 | Primary content |
| `--sol-base1` | #586e75 | Emphasis |
| `--sol-cyan` | #2aa198 | START button |
| `--sol-blue` | #268bd2 | Links, timer |
| `--sol-green` | #859900 | Success message |

## License

This is a clone for educational and automation testing purposes. The original RPA Challenge is created by UiPath.

## Version

0.2.1 - Includes rpachallenge.com clone with GitHub Pages support
