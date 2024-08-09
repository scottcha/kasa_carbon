from kasa import Discover, SmartPlug, SmartStrip
from kasa_carbon.interfaces.monitor_api import MonitorAPI
from kasa_carbon.modules.database import Database
from kasa_carbon.interfaces.datastore_api import DatastoreAPI
from kasa_carbon.modules.electricitymaps_api import ElectricityMapAPI
from kasa_carbon.modules.energy_usage import EnergyUsage
import time
from datetime import datetime, timezone

from kasa_carbon.modules.generic_monitor import monitor_energy_use

class KasaMonitor(MonitorAPI):
    def __init__(self, api_key, local_lat=None, local_lon=None, local_grid_id=None, co2_api_provider="ElectricityMaps", em_cache_expiry_mins=30):
        self.devices = []
        self.lat = local_lat 
        self.lon = local_lon 
        self.grid_id = None
        if (local_lat is None or local_lon is None) and local_grid_id is None:
            raise ValueError("Must provide either local_lat/local_lon or local_grid_id")
        elif local_grid_id is not None:
            self.grid_id = local_grid_id
        #else should be just use local_lat/local_lon

        if co2_api_provider == "ElectricityMaps":
            self.co2_api = ElectricityMapAPI(em_api_key=api_key, em_cache_expiry_mins=em_cache_expiry_mins)
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


    async def monitor_energy_use_continuously(self, db: DatastoreAPI, delay: int, timeout: int=None):
        '''
        Monitor energy use continuously and store the data in the database.

        DB Schema:
        device VARCHAR(255) NOT NULL,
        timestamp TIMESTAMPTZ NOT NULL,
        power_draw_watts real NOT NULL,
        avg_emitted_mgco2e real,
        grid_carbon_intensity_gco2perkwhr real,
        PRIMARY KEY (device, timestamp)

        Args:
            db (Database): The database to store the energy use data in.
            delay (int): The number of seconds to wait between each update.
            timeout (int, optional): The number of seconds to run the monitor for. Defaults to None, which will run forever.
        
        Returns:
            None
        '''
        await monitor_energy_use(self.monitor_energy_use_once, self._get_co2_data, db, delay, timeout)