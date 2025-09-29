"""
Configuration file for WordPress Data Collection Agent
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # WordPress Admin URL
    WP_ADMIN_URL = "https://dtcrxoptics.com/wp-admin/admin.php?page=gf_entries&view=entries&id=21"
    
    # Login credentials (set these in .env file)
    WP_USERNAME = os.getenv('WP_USERNAME')
    WP_PASSWORD = os.getenv('WP_PASSWORD')
    
    # Browser settings
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
    IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', '10'))
    PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
    
    # Data extraction settings
    MAX_ENTRIES = int(os.getenv('MAX_ENTRIES', '1000'))
    ENTRIES_PER_PAGE = int(os.getenv('ENTRIES_PER_PAGE', '20'))
    
    # Output settings
    OUTPUT_FORMAT = os.getenv('OUTPUT_FORMAT', 'csv')  # csv, json, excel
    OUTPUT_FILE = os.getenv('OUTPUT_FILE', 'wordpress_entries.csv')
    
    # Retry settings
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', '2'))
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.WP_USERNAME or not cls.WP_PASSWORD:
            raise ValueError("WordPress username and password must be set in .env file")
        return True
