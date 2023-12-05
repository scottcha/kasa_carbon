#!/usr/bin/env python3

import asyncio
import argparse
import config
from modules import kasa_monitor, database, file_storage
from dotenv import load_dotenv, find_dotenv

async def main():
    #print(find_dotenv())
    #print(load_dotenv())
    load_dotenv(find_dotenv())

    parser = argparse.ArgumentParser(description='Choose storage method.')
    parser.add_argument('--storage', choices=['database', 'file'], default='database', help='Storage method')
    parser.add_argument('--file-path', default='energy_usage.csv', help='File path for file storage')
    parser.add_argument('--file-mode', choices=['append', 'overwrite'], default='append', help='File mode for file storage append will continuously append and overwrite will only keep the most recent value')
    args = parser.parse_args()

    kasa = kasa_monitor.KasaMonitor()

    #print contents of confg.db_config
    print(config.db_config)

    if args.storage == 'file':
        storage = file_storage.FileStorage(args.file_path, args.file_mode)
    else: #database is default
        storage = database.Database(config.db_config)

    # Monitor energy use continuously in a subthread to avoid blocking the main thread
    energy_use_task = asyncio.create_task(kasa.monitor_energy_use_continuously(storage, delay=config.UPDATE_INTERVAL_SEC))
    
    while True:
        if energy_use_task.done():
            print("The energy monitoring task has completed.")
        else:
            print("The energy monitoring task is still running.")

        # view the current database values
        print(await storage.read_usage())

        # Wait for next update
        await asyncio.sleep(config.UPDATE_INTERVAL_SEC)

if __name__ == "__main__":
    asyncio.run(main())