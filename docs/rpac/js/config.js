// Parse URL parameters for dynamic configuration
function getUrlParam(name, defaultValue) {
  const urlParams = new URLSearchParams(window.location.search);
  const value = urlParams.get(name);
  return value !== null ? parseInt(value, 10) : defaultValue;
}

const CONFIG = {
  // Allow dynamic rounds via URL parameter: ?rounds=5
  // Falls back to data length, or 10 if data is not yet loaded
  TOTAL_ROUNDS: getUrlParam('rounds', 10),
  FIELDS: [
    { name: 'labelFirstName', label: 'First Name', excelCol: 'first_name' },
    { name: 'labelLastName', label: 'Last Name', excelCol: 'last_name' },
    { name: 'labelPhone', label: 'Phone Number', excelCol: 'phone' },
    { name: 'labelEmail', label: 'Email', excelCol: 'email' },
    { name: 'labelAddress', label: 'Address', excelCol: 'address' },
    { name: 'labelCompanyName', label: 'Company Name', excelCol: 'company_name' },
    { name: 'labelRole', label: 'Role in Company', excelCol: 'role' }
  ]
};
