import asyncio
import config
from modules import kasa_monitor, grafana_display, electricitymaps_api, watttime_api, database
from interfaces import carbon_api
import os
from dotenv import load_dotenv

async def main():
    load_dotenv()
    # Create instances of each module
    kasa = kasa_monitor.KasaMonitor()
    #grafana = grafana_display.GrafanaDisplay()
    db = database.Database(config.db_config)

    # Monitor energy use continuously in a subthread to avoid blocking the main thread
    energy_use_task = asyncio.create_task(kasa.monitor_energy_use_continuously(db, delay=config.UPDATE_INTERVAL_SEC))
    
    while True:
        if energy_use_task.done():
            print("The energy monitoring task has completed.")
        else:
            print("The energy monitoring task is still running.")

        # view the current database values
        print(await db.read_usage())

        # Wait for next update
        await asyncio.sleep(config.UPDATE_INTERVAL_SEC)

if __name__ == "__main__":
    asyncio.run(main())