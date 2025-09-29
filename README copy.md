# 🌞 WordPress Data Agent & NetSuite Integration ☀️

*Because manually copying data between systems is so 2010!* 😄

## What's This Magic? ✨

This project is your personal data wizard that automatically:
- 🎯 Logs into WordPress admin (no more CAPTCHA headaches!)
- 📊 Extracts Gravity Forms entries like a digital archaeologist
- 🚀 Creates NetSuite Sales Orders faster than you can say "automation"
- ☕ Gives you time back to enjoy that coffee instead of data entry

## 🎪 The Show Must Go On

**WordPress Admin**: https://dtcrxoptics.com/wp-admin/admin.php?page=gf_entries&view=entries&id=21  
**NetSuite**: https://system.netsuite.com/pages/customerlogin.jsp?country=US

## 🏗️ Project Structure (The Cast of Characters)

```
wordpress_data_agent/
├── config.py                    # 🎛️ The control center
├── login_agent.py               # 🕵️ The stealth login ninja
├── export_first_entry.py        # 🎯 The first-pick specialist
├── export_entry_by_text.py     # 📝 The text whisperer
├── map_to_netsuite_so.py       # 🔄 The data transformer
├── netsuite_login.py           # 🚪 The NetSuite gatekeeper
├── netsuite_create_so.py       # 🛒 The sales order creator
├── parse_saved_entry.py        # 🔍 The HTML detective
├── requirements.txt            # 📦 The dependency list
├── run_login.sh               # 🎬 The director's cut
└── ENV_EXAMPLE.txt            # 📋 The template superstar
```

## 🚀 Let's Get This Party Started!

### 1️⃣ Python Environment Setup
```bash
# Activate your virtual environment (like putting on your coding cape!)
source /Users/tonnguyen/venv/bin/activate

# Install the magic ingredients
pip install -r /Users/tonnguyen/wordpress_data_agent/requirements.txt
```

### 2️⃣ Environment Variables (The Secret Sauce)
Create a `.env` file and add your credentials:
```bash
# WordPress credentials (your admin superpowers)
WP_USERNAME=your_username_here
WP_PASSWORD=your_password_here

# NetSuite credentials (your business empire access)
NS_USERNAME=your_netsuite_email@domain.com
NS_PASSWORD=your_netsuite_password
NS_LOGIN_URL=https://system.netsuite.com/pages/customerlogin.jsp?country=US

# Optional settings (the fine-tuning knobs)
HEADLESS_MODE=False
IMPLICIT_WAIT=10
PAGE_LOAD_TIMEOUT=45
ENTRY_ID=29990
```

## 🎭 The Grand Performance (Usage)

### 🎪 Act 1: WordPress Login & Navigation
```bash
# The classic approach (prompts for credentials like a polite butler)
python /Users/tonnguyen/wordpress_data_agent/login_agent.py

# The environment variable approach (like having a VIP pass)
WP_USERNAME=chaosadmin WP_PASSWORD='Pwalsh123/' python /Users/tonnguyen/wordpress_data_agent/login_agent.py

# The helper script approach (the red carpet treatment)
/Users/tonnguyen/wordpress_data_agent/run_login.sh
```

### 🎪 Act 2: Export Entry Data (The Data Harvest)
```bash
# Export the first entry (like picking the ripest fruit)
python /Users/tonnguyen/wordpress_data_agent/export_first_entry.py

# Export a specific entry by ID (the precision strike)
ENTRY_ID=29990 python /Users/tonnguyen/wordpress_data_agent/export_entry_by_text.py

# Export with CLI argument (the direct approach)
python /Users/tonnguyen/wordpress_data_agent/export_entry_by_text.py 29993
```

### 🎪 Act 3: Convert to NetSuite Format (The Transformation)
```bash
# Convert entry JSON to NetSuite Sales Order CSV (like a data alchemist)
python /Users/tonnguyen/wordpress_data_agent/map_to_netsuite_so.py /path/to/entry_29990_*.json
```

### 🎪 Act 4: NetSuite Integration (The Grand Finale)
```bash
# Login to NetSuite (the VIP entrance)
NS_USERNAME=user@domain.com NS_PASSWORD=pass123 python /Users/tonnguyen/wordpress_data_agent/netsuite_login.py

# Create Sales Order from entry (the money-making moment!)
NS_USERNAME=user@domain.com NS_PASSWORD=pass123 python /Users/tonnguyen/wordpress_data_agent/netsuite_create_so.py /path/to/entry_29990_*.json
```

## 🎬 The Complete Blockbuster Workflow
```bash
# Scene 1: Export entry 29990 (the data extraction heist)
WP_USERNAME=chaosadmin WP_PASSWORD='Pwalsh123/' ENTRY_ID=29990 python /Users/tonnguyen/wordpress_data_agent/export_entry_by_text.py

# Scene 2: Convert to NetSuite format (the data transformation montage)
python /Users/tonnguyen/wordpress_data_agent/map_to_netsuite_so.py /Users/tonnguyen/wordpress_data_agent/entry_29990_*.json

# Scene 3: Create NetSuite Sales Order (the triumphant finale!)
NS_USERNAME=tonnguyenthe291the@gmail.com NS_PASSWORD=ChaosSupplies123 python /Users/tonnguyen/wordpress_data_agent/netsuite_create_so.py /Users/tonnguyen/wordpress_data_agent/entry_29990_*.json
```

## 🎁 The Treasure Chest (Output Files)

For each entry export, you'll get these digital treasures:
- `entry_<ID>_<timestamp>.json` - 📊 Structured entry data (the organized version)
- `entry_<ID>_<timestamp>.csv` - 📋 CSV format with label/value pairs (the spreadsheet lover's dream)
- `entry_visible_<timestamp>.txt` - 📝 Raw visible text from the page (the behind-the-scenes footage)
- `netsuite_sales_order_<ID>_<timestamp>.csv` - 🛒 NetSuite-ready Sales Order CSV (the money-making file!)

## 🔄 The Data Transformation Magic

**WordPress Entry → NetSuite Sales Order** (like a digital makeover!):
- **Entity**: Employee Email (or First Name + Last Name) - *Who's the customer?*
- **Item**: Product name - *What are they buying?*
- **Quantity**: Numeric quantity - *How many do they want?*
- **Memo**: Form name, Entry ID, Employee ID, Site, Phone (pipe-separated) - *All the juicy details!*

## 🎭 The Cast of Characters (Scripts Overview)

- `login_agent.py`: 🕵️ The stealth login ninja (handles CAPTCHA/2FA like a pro)
- `export_entry_by_text.py`: 📝 The text whisperer (scrapes data using visible text parsing)
- `map_to_netsuite_so.py`: 🔄 The data transformer (converts entry JSON to NetSuite CSV format)
- `netsuite_create_so.py`: 🛒 The sales order creator (automates NetSuite Sales Order creation)
- `parse_saved_entry.py`: 🔍 The HTML detective (debug tool for HTML parsing)

## 🚨 When Things Go Wrong (Troubleshooting)

### 🚗 Chrome/Driver Issues
- Make sure Chrome is installed locally (it's like having a car in the garage!)
- Scripts use Selenium Manager for automatic driver resolution (the autopilot feature)

### 🔐 Login Failures
- Check credentials in environment variables (like checking your keys before leaving)
- For CAPTCHA/2FA, use visible browser mode (`HEADLESS_MODE=False`) - *Sometimes you need to see what's happening!*
- Verify target URLs are accessible (like checking if the store is open)

### 📊 Data Extraction Issues
- Check if entry ID exists and is accessible (like making sure the door isn't locked)
- Review generated text dumps for parsing issues (the detective work)
- Use visible browser mode to inspect page structure (the magnifying glass approach)

### 🏢 NetSuite Integration Issues
- Verify NetSuite credentials and permissions (like checking your VIP pass)
- Check if Sales Order creation is enabled for your role (the permission check)
- Review browser console for JavaScript errors (the technical detective work)

## 🎛️ Environment Variables Reference (The Control Panel)

**Required (The Essentials):**
- `WP_USERNAME`: WordPress admin username (your admin superpowers)
- `WP_PASSWORD`: WordPress admin password (the secret handshake)
- `NS_USERNAME`: NetSuite login email (your business empire access)
- `NS_PASSWORD`: NetSuite password (the golden key)

**Optional (The Fine-Tuning Knobs):**
- `HEADLESS_MODE`: Browser visibility (True/False, default: False) - *Sometimes you want to see the magic!*
- `IMPLICIT_WAIT`: Selenium wait timeout in seconds (default: 10) - *The patience setting*
- `PAGE_LOAD_TIMEOUT`: Page load timeout in seconds (default: 45) - *The "how long to wait" setting*
- `ENTRY_ID`: Specific entry ID to export - *The target selection*
- `NS_LOGIN_URL`: NetSuite login URL (default: system login page) - *The entrance door*

## 🌟 Pro Tips (The Wisdom)

- All scripts support both environment variables and CLI arguments (flexibility is key!)
- Visible browser mode is recommended for first-time setup and debugging (see the magic happen!)
- Generated files include timestamps to avoid overwrites (no more "oops, I overwrote my work!")
- Scripts handle common WordPress and NetSuite UI variations (they're adaptable like chameleons!)

---

*Happy automating! May your data flow smoothly and your coffee stay hot! ☕✨*
