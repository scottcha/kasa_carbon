#!/usr/bin/env python3

import asyncio
import argparse
import os
from kasa_carbon.modules import kasa_monitor, database, file_storage
from dotenv import load_dotenv, find_dotenv

async def main():
    load_dotenv(find_dotenv())

    parser = argparse.ArgumentParser(description='kasa-carbon arguments')
    parser.add_argument('--storage', choices=['database', 'file'], default='database', help='Storage method')
    parser.add_argument('--file-path', default='energy_usage.csv', help='File path for file storage')
    parser.add_argument('--file-mode', choices=['append', 'overwrite'], default='append', help='File mode for file storage append will continuously append and overwrite will only keep the most recent value')
    parser.add_argument("--db_host", default=os.getenv("DB_HOST"), help="Database host")
    parser.add_argument("--db_port", default=os.getenv("DB_PORT"), type=int, help="Database port")
    parser.add_argument("--db_user", default=os.getenv("DB_USER"), help="Database user")
    parser.add_argument("--db_password", default=os.getenv("DB_PASSWORD"), help="Database password")
    parser.add_argument("--db_name", default=os.getenv("DB_NAME"), help="Database name")
    parser.add_argument("--db_view_user", default=os.getenv("DB_VIEW_USER"), help="Database view user")
    parser.add_argument("--em_api_key", default=os.getenv("EM_API_KEY"), help="API key")
    parser.add_argument("--em_cache_expiry_mins", default=os.getenv("EM_CACHE_EXPIRY_MINS"), type=int, help="Carbon Data cache expiry in minutes")
    parser.add_argument("--local_lat", default=os.getenv("LOCAL_LAT"), type=float, help="Local latitude")
    parser.add_argument("--local_lon", default=os.getenv("LOCAL_LON"), type=float, help="Local longitude")
    parser.add_argument("--update_interval_sec", default=15, type=int, help="Update interval in seconds")


    args = parser.parse_args()

    # Set the values as global constants
    DB_HOST = args.db_host
    DB_PORT = args.db_port
    DB_USER = args.db_user
    DB_NAME = args.db_name
    DB_VIEW_USER = args.db_view_user
    EM_API_KEY = args.em_api_key
    EM_CACHE_EXPIRY_MINS = args.em_cache_expiry_mins
    LOCAL_LAT = args.local_lat
    LOCAL_LON = args.local_lon

    # Configuration for General API
    API_KEY = EM_API_KEY 
    API_TYPE = "ElectricityMaps"  # or "watttime"

    # Update interval in seconds
    UPDATE_INTERVAL_SEC = args.update_interval_sec

    # database connection information
    db_config = {
        "user": args.db_user,
        "password": args.db_password,
        "database": args.db_name,
        "host": args.db_host,
        "port": args.db_port,
    }
    kasa = kasa_monitor.KasaMonitor(api_key = API_KEY, local_lon=LOCAL_LON, local_lat=LOCAL_LAT, co2_api_provider=API_TYPE, em_cache_expiry_mins=EM_CACHE_EXPIRY_MINS)

    if args.storage == 'file':
        storage = file_storage.FileStorage(args.file_path, args.file_mode)
    else: #database is default
        storage = database.Database(db_config)

    # Monitor energy use continuously in a subthread to avoid blocking the main thread
    energy_use_task = asyncio.create_task(kasa.monitor_energy_use_continuously(storage, delay=UPDATE_INTERVAL_SEC))
    
    while True:
        if energy_use_task.done():
            print("The energy monitoring task has completed.")
        else:
            print("The energy monitoring task is still running.")

        # view the current database values
        print(await storage.read_usage())

        # Wait for next update
        await asyncio.sleep(UPDATE_INTERVAL_SEC)

def main_wrapper():
    asyncio.run(main())

if __name__ == "__main__":
    main_wrapper()