/**
 * Data Table Manager
 * Renders CHALLENGE_DATA as an HTML table (single source of truth)
 */

class DataTableManager {
  constructor(data, maxRounds) {
    this.allData = data;
    this.maxRounds = maxRounds;
    this.data = data.slice(0, maxRounds); // Use only the requested number of rounds
    this.isVisible = false;

    console.log(`[DATA-TABLE] Using ${this.data.length} records (max: ${maxRounds})`);
  }

  render() {
    const table = document.getElementById('dataTable');
    if (!table) return;

    // Build table HTML
    const headers = ['#', 'First Name', 'Last Name', 'Phone Number', 'Email', 'Address', 'Company Name', 'Role in Company'];

    let html = '<thead><tr>';
    headers.forEach(header => {
      html += `<th>${header}</th>`;
    });
    html += '</tr></thead><tbody>';

    this.data.forEach((record, index) => {
      html += '<tr>';
      html += `<td>${index + 1}</td>`;
      html += `<td>${record.first_name}</td>`;
      html += `<td>${record.last_name}</td>`;
      html += `<td>${record.phone}</td>`;
      html += `<td>${record.email}</td>`;
      html += `<td>${record.address}</td>`;
      html += `<td>${record.company_name}</td>`;
      html += `<td>${record.role}</td>`;
      html += '</tr>';
    });

    html += '</tbody>';
    table.innerHTML = html;

    console.log(`[DATA-TABLE] Rendered table with ${this.data.length} rows`);
  }

  toggle() {
    const container = document.getElementById('dataTableContainer');
    if (!container) return;

    this.isVisible = !this.isVisible;
    container.style.display = this.isVisible ? 'block' : 'none';
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  // Get the actual number of rounds being used (from config.js)
  const actualRounds = CONFIG.TOTAL_ROUNDS;

  const dataTableManager = new DataTableManager(CHALLENGE_DATA, actualRounds);
  dataTableManager.render();

  // Wire up toggle button
  const toggleBtn = document.getElementById('toggleDataBtn');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => dataTableManager.toggle());
  }

  // Make dataTableManager globally accessible for excel-generator
  window.dataTableManager = dataTableManager;
});
