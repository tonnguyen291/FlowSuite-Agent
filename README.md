WordPress Data Agent & NetSuite Integration ☀️

Because manually copying data between systems is so 2010! 😄

What's This Magic? ✨
This project is your personal data wizard that automatically:

🎯 Logs into WordPress admin (no more CAPTCHA headaches!)
📊 Extracts Gravity Forms entries like a digital archaeologist
🚀 Creates NetSuite Sales Orders faster than you can say "automation"
☕ Gives you time back to enjoy that coffee instead of data entry
WordPress Data Agent & NetSuite Integration

Overview
This project automates the extraction of Gravity Forms entries from WordPress admin and creates corresponding Sales Orders in NetSuite. It includes login automation, data scraping, and NetSuite integration scripts.

Target System
- WordPress Admin: https://dtcrxoptics.com/wp-admin/admin.php?page=gf_entries&view=entries&id=21
- NetSuite: https://system.netsuite.com/pages/customerlogin.jsp?country=US

Project Structure
```
wordpress_data_agent/
├── config.py                    # Configuration and environment variables
├── login_agent.py               # WordPress login automation
├── export_first_entry.py        # Export first entry from list
├── export_entry_by_text.py     # Export specific entry by ID (text-based)
├── map_to_netsuite_so.py       # Convert entry JSON to NetSuite CSV
├── netsuite_login.py           # NetSuite login automation
├── netsuite_create_so.py       # Create NetSuite Sales Order from entry
├── parse_saved_entry.py        # Parse saved HTML for debugging
├── requirements.txt            # Python dependencies
├── run_login.sh               # Helper script to run login agent
└── ENV_EXAMPLE.txt            # Environment variables template
```

Setup

1) Python Environment
```bash
# Activate virtual environment
source /Users/tonnguyen/venv/bin/activate

# Install dependencies
pip install -r /Users/tonnguyen/wordpress_data_agent/requirements.txt
```

2) Environment Variables
Create a `.env` file in the project directory with:
```
# WordPress credentials
WP_USERNAME=your_username_here
WP_PASSWORD=your_password_here

# NetSuite credentials  
NS_USERNAME=your_netsuite_email@domain.com
NS_PASSWORD=your_netsuite_password
NS_LOGIN_URL=https://system.netsuite.com/pages/customerlogin.jsp?country=US

# Optional settings
HEADLESS_MODE=False
IMPLICIT_WAIT=10
PAGE_LOAD_TIMEOUT=45
ENTRY_ID=29990
```

Usage

1) WordPress Login & Navigation
```bash
# Basic login (prompts for credentials if not in env)
python /Users/tonnguyen/wordpress_data_agent/login_agent.py

# With environment variables
WP_USERNAME=chaosadmin WP_PASSWORD='Pwalsh123/' python /Users/tonnguyen/wordpress_data_agent/login_agent.py

# Using helper script
/Users/tonnguyen/wordpress_data_agent/run_login.sh
```

2) Export Entry Data
```bash
# Export first entry from the list
python /Users/tonnguyen/wordpress_data_agent/export_first_entry.py

# Export specific entry by ID
ENTRY_ID=29990 python /Users/tonnguyen/wordpress_data_agent/export_entry_by_text.py

# Export with CLI argument
python /Users/tonnguyen/wordpress_data_agent/export_entry_by_text.py 29993
```

3) Convert to NetSuite Format
```bash
# Convert entry JSON to NetSuite Sales Order CSV
python /Users/tonnguyen/wordpress_data_agent/map_to_netsuite_so.py /path/to/entry_29990_*.json
```

4) NetSuite Integration
```bash
# Login to NetSuite
NS_USERNAME=user@domain.com NS_PASSWORD=pass123 python /Users/tonnguyen/wordpress_data_agent/netsuite_login.py

# Create Sales Order from entry
NS_USERNAME=user@domain.com NS_PASSWORD=pass123 python /Users/tonnguyen/wordpress_data_agent/netsuite_create_so.py /path/to/entry_29990_*.json
```

Complete Workflow Example
```bash
# 1. Export entry 29990
WP_USERNAME=chaosadmin WP_PASSWORD='Pwalsh123/' ENTRY_ID=29990 python /Users/tonnguyen/wordpress_data_agent/export_entry_by_text.py

# 2. Convert to NetSuite format
python /Users/tonnguyen/wordpress_data_agent/map_to_netsuite_so.py /Users/tonnguyen/wordpress_data_agent/entry_29990_*.json

# 3. Create NetSuite Sales Order
NS_USERNAME=tonnguyenthe291the@gmail.com NS_PASSWORD=ChaosSupplies123 python /Users/tonnguyen/wordpress_data_agent/netsuite_create_so.py /Users/tonnguyen/wordpress_data_agent/entry_29990_*.json
```

Output Files

For each entry export, the following files are generated:
- `entry_<ID>_<timestamp>.json` - Structured entry data
- `entry_<ID>_<timestamp>.csv` - CSV format with label/value pairs
- `entry_visible_<timestamp>.txt` - Raw visible text from the page
- `netsuite_sales_order_<ID>_<timestamp>.csv` - NetSuite-ready Sales Order CSV

Data Mapping

WordPress Entry → NetSuite Sales Order:
- Entity: Employee Email (or First Name + Last Name)
- Item: Product name
- Quantity: Numeric quantity
- Memo: Form name, Entry ID, Employee ID, Site, Phone (pipe-separated)

Scripts Overview

- `login_agent.py`: Handles WordPress login with CAPTCHA/2FA support
- `export_entry_by_text.py`: Scrapes entry data using visible text parsing
- `map_to_netsuite_so.py`: Converts entry JSON to NetSuite CSV format
- `netsuite_create_so.py`: Automates NetSuite Sales Order creation
- `parse_saved_entry.py`: Debug tool for HTML parsing

Troubleshooting

1) Chrome/Driver Issues
- Ensure Chrome is installed locally
- Scripts use Selenium Manager for automatic driver resolution

2) Login Failures
- Check credentials in environment variables
- For CAPTCHA/2FA, use visible browser mode (`HEADLESS_MODE=False`)
- Verify target URLs are accessible

3) Data Extraction Issues
- Check if entry ID exists and is accessible
- Review generated text dumps for parsing issues
- Use visible browser mode to inspect page structure

4) NetSuite Integration Issues
- Verify NetSuite credentials and permissions
- Check if Sales Order creation is enabled for your role
- Review browser console for JavaScript errors

Environment Variables Reference

Required:
- `WP_USERNAME`: WordPress admin username
- `WP_PASSWORD`: WordPress admin password
- `NS_USERNAME`: NetSuite login email
- `NS_PASSWORD`: NetSuite password

Optional:
- `HEADLESS_MODE`: Browser visibility (True/False, default: False)
- `IMPLICIT_WAIT`: Selenium wait timeout in seconds (default: 10)
- `PAGE_LOAD_TIMEOUT`: Page load timeout in seconds (default: 45)
- `ENTRY_ID`: Specific entry ID to export
- `NS_LOGIN_URL`: NetSuite login URL (default: system login page)

Notes
- All scripts support both environment variables and CLI arguments
- Visible browser mode is recommended for first-time setup and debugging
- Generated files include timestamps to avoid overwrites
- Scripts handle common WordPress and NetSuite UI variations
