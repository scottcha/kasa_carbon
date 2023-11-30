import os
# Configuration for Kasa

# Configuration for Grafana
GRAFANA_URL = "your_grafana_url"
GRAFANA_API_KEY = "your_grafana_api_key"

# Configuration for General API
API_KEY = "your_api_key"
API_TYPE = "electricitymaps"  # or "watttime"

# Update interval in seconds
UPDATE_INTERVAL_SEC = 15  # second interval to update 

# database connection information
db_config = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}