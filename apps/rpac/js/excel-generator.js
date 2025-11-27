/**
 * Excel Generator
 * Generates Excel file on-the-fly from CHALLENGE_DATA using SheetJS
 */

class ExcelGenerator {
  /**
   * Generate and download Excel file
   * Uses the SAME data as shown in the HTML table (respects rounds parameter)
   */
  generate() {
    // Get data from the data table manager (which already respects rounds parameter)
    const data = window.dataTableManager ? window.dataTableManager.data : CHALLENGE_DATA;

    console.log(`[EXCEL] Generating Excel file with ${data.length} records...`);

    // Create worksheet data
    const headers = ['First Name', 'Last Name', 'Phone Number', 'Email', 'Address', 'Company Name', 'Role in Company'];

    const wsData = [headers];

    // Add data rows
    data.forEach(record => {
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
  const excelGenerator = new ExcelGenerator();

  // Wire up generate button
  const generateBtn = document.getElementById('generateExcelBtn');
  if (generateBtn) {
    generateBtn.addEventListener('click', () => excelGenerator.generate());
  }
});
