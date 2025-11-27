"""Generate challenge.xlsx for RPA Challenge clone.

This script creates the Excel file with the same data used in the challenge.
Run with: python generate_excel.py
"""

import openpyxl
from pathlib import Path

# Same data as js/data.js
data = [
    ["John", "Smith", "40716543298", "jsmith@itsolutions.co.uk", "98 North Road", "IT Solutions", "Analyst"],
    ["Jane", "Dorsey", "40791345621", "jdorsey@medcare.com", "11 Crown Street", "MediCare", "Medical Engineer"],
    ["Albert", "Kipling", "40735416854", "kipling@waterfront.com", "22 Guild Street", "Waterfront", "Accountant"],
    ["Michael", "Robertson", "40733652145", "mrobertson@medcare.com", "83 Jan Road", "MediCare", "IT Specialist"],
    ["Doug", "Derrick", "40794485865", "dderrick@timepath.co.uk", "99 Shire Oak Road", "Timepath Inc.", "Analyst"],
    ["Jessie", "Marlowe", "40733845219", "jmarlowe@aperture.us", "27 Cheshire Street", "Aperture Inc.", "Scientist"],
    ["Stan", "Hamm", "40712462257", "shamm@sugarwell.org", "10 Dam Road", "Sugarwell", "Advisor"],
    ["Michelle", "Norton", "40700854721", "mnorton@gadget.co.uk", "14 Bilton View", "Gadget UK", "Designer"],
    ["Stacy", "Shelby", "40735416766", "sshelby@techdev.com", "19 Peterborough Avenue", "TechDev", "HR Manager"],
    ["Lara", "Palmer", "40730141970", "lpalmer@recreate.ru", "87 Horsefair Green", "Recreate Rus", "Programmer"]
]

# Headers (exact column names as per schema)
headers = ["First Name", "Last Name", "Phone Number", "Email", "Address", "Company Name", "Role in Company"]

# Create workbook and worksheet
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Challenge"

# Write headers
ws.append(headers)

# Write data rows
for row in data:
    ws.append(row)

# Save to assets directory
output_path = Path(__file__).parent / "assets" / "challenge.xlsx"
output_path.parent.mkdir(exist_ok=True)
wb.save(output_path)

print(f"Created: {output_path}")
print(f"Records: {len(data)}")
print(f"Fields: {len(headers)}")
