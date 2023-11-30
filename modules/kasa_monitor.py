from kasa import Discover, SmartPlug, SmartStrip
from modules.database import Database
from modules.electricitymaps_api import ElectricityMapAPI
import asyncio
import time, os
from datetime import datetime, timezone

class KasaMonitor:
    def __init__(self, local_lat=None, local_lon=None, local_grid_id=None, co2_api_provider="ElectricityMaps"):
        self.devices = []
        self.lat = None
        self.lon = None
        self.grid_id = None
        if (local_lat is None or local_lon is None) and local_grid_id is None:
            #TODO use a geoip service to get the lat/lon
            self.lat = os.getenv("LOCAL_LAT")
            self.lon = os.getenv("LOCAL_LON")
        elif local_grid_id is not None:
            self.grid_id = local_grid_id
        else:
            raise ValueError("Must provide either local_lat/local_lon or local_grid_id")

        if co2_api_provider == "ElectricityMaps":
            self.co2_api = ElectricityMapAPI()
        else:
            raise ValueError("co2_api_provider must be 'EM' until others are supported")        

    async def discover_devices(self):
        # Discover Kasa devices on the network
        self.devices = await Discover.discover()

    async def monitor_energy_use_once(self):
        energy_values = {}

        #assert discover_devices has been called
        if len(self.devices) == 0:
            await self.discover_devices()

        for addr, device in self.devices.items():
            await device.update()
            if isinstance(device, SmartStrip):
                for i, plug in enumerate(device.children):
                    if plug.has_emeter:
                        emeter_realtime = plug.emeter_realtime
                        energy_values[f"{device.alias + '-' + plug.alias}"] = emeter_realtime["power"]
            elif device.has_emeter:
                emeter_realtime = device.emeter_realtime
                energy_values[device.alias] = emeter_realtime["power"]

        return energy_values

    #get carbon data by either grid or lat/lon
    async def _get_co2_data(self):
        if self.grid_id is not None:
            return await self.co2_api.get_co2_by_gridid(self.grid_id)
        else:
            return await self.co2_api.get_co2_by_latlon(self.lat, self.lon) 

    async def monitor_energy_use_continuously(self, db, delay, timeout=None):
        start_time = time.time()

        try:
            while True:
                energy_values = await self.monitor_energy_use_once()

                #Get average CO2 from API
                co2 = await self._get_co2_data()
                for device, power in energy_values.items():

                    energy_usage = {"device": device, "timestamp": datetime.now(timezone.utc), "power": power, "avg_mg_co2": co2}
                    await db.write_usage(energy_usage)

                if timeout is not None and time.time() - start_time >= timeout:
                    break

                time.sleep(delay)
        finally:
            await db.close()