/**
 * Excel Generator
 * Generates Excel file on-the-fly from CHALLENGE_DATA using SheetJS
 */

class ExcelGenerator {
  constructor(data) {
    this.data = data;
  }

  /**
   * Generate and download Excel file
   */
  generate() {
    console.log('[EXCEL] Generating Excel file from CHALLENGE_DATA...');

    // Create worksheet data
    const headers = ['First Name', 'Last Name', 'Phone Number', 'Email', 'Address', 'Company Name', 'Role in Company'];

    const wsData = [headers];

    // Add data rows
    this.data.forEach(record => {
      wsData.push([
        record.first_name,
        record.last_name,
        record.phone,
        record.email,
        record.address,
        record.company_name,
        record.role
      ]);
    });

    // Create workbook and worksheet
    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.aoa_to_sheet(wsData);

    // Set column widths
    ws['!cols'] = [
      { wch: 15 },  // First Name
      { wch: 15 },  // Last Name
      { wch: 15 },  // Phone Number
      { wch: 30 },  // Email
      { wch: 25 },  // Address
      { wch: 20 },  // Company Name
      { wch: 20 }   // Role in Company
    ];

    // Add worksheet to workbook
    XLSX.utils.book_append_sheet(wb, ws, "Challenge");

    // Generate Excel file and trigger download
    XLSX.writeFile(wb, "challenge.xlsx");

    console.log('[EXCEL] Excel file generated and downloaded');
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  const excelGenerator = new ExcelGenerator(CHALLENGE_DATA);

  // Wire up generate button
  const generateBtn = document.getElementById('generateExcelBtn');
  if (generateBtn) {
    generateBtn.addEventListener('click', () => excelGenerator.generate());
  }
});
