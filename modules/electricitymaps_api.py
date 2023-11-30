
import aiohttp
from interfaces.carbon_api import CarbonAPI
import os 
from datetime import datetime, timezone, timedelta
import json

class ElectricityMapAPI(CarbonAPI):
    BASE_URL = "https://api-access.electricitymaps.com/free-tier/carbon-intensity/latest"
    CACHE_FILE = "em_cache.json"

    def __init__(self, co2_time_threshold_mins=120, clear_cache=False):
        self.api_key = os.getenv("EM_API_KEY")
        self.co2_time_threshold_mins = co2_time_threshold_mins
        self.CACHE_EXPIRY = timedelta(int(os.getenv("EM_CACHE_EXPIRY_MINS")))
        if clear_cache:
            self._clear_cache()
        else:
            self._load_cache()
    
    def _load_cache(self):
        if os.path.exists(self.CACHE_FILE):
            with open(self.CACHE_FILE, 'r') as f:
                cache = json.load(f)
                # Convert the keys from strings to dictionaries and the timestamps from strings to datetime objects
                self.cache = {key: [value[0], datetime.fromisoformat(value[1])] for key, value in cache.items()}
        else:
            self.cache = {}

    def _save_cache(self):
        # Convert the timestamps from datetime objects to strings
        cache = {key: [value[0], value[1].isoformat()] for key, value in self.cache.items()}
        with open(self.CACHE_FILE, 'w') as f:
            json.dump(cache, f)

    def _clear_cache(self):
        self.cache = {}
        self._save_cache()

    async def get_co2_by_gridid(self, grid_id: str) -> float:
        '''
        Get the current CO2 emission rate per kWh for a specific location, identified by grid ID.
        Will use a local cache to store the data for 30 minutes to ease the load on the API.

        Args:
            grid_id (str): The grid ID of the specific location.

        Returns:
            float: The CO2 emission rate in gCO2/kWh if data is available and less than 120 minutes old, otherwise returns None.
        '''
        params = {"zone": grid_id} 
        return await self._get_co2_data(params)

    async def get_co2_by_latlon(self, lat: float, lon: float) -> float:
        '''
        Get the current CO2 emission rate per kWh for a specific location, identified by latitude and longitude.
        Will use a local cache to store the data for 30 minutes to ease the load on the API.

        Args:
            lat (float): The latitude of the location.
            lon (float): The longitude of the location.

        Returns:
            float: The CO2 emission rate in gCO2/kWh if data is available and less than 120 minutes old, otherwise returns None.
        '''
        params = {"lat": lat, "lon": lon}
        return await self._get_co2_data(params)

    async def _get_co2_data(self, params) -> float:
        # Check if the data is in the cache and is less than 30 minutes old
        # Convert the params dictionary to a string to use as a key
        cache_key = '_'.join(str(v) for v in params.values())
        if cache_key in self.cache and datetime.now(timezone.utc) - self.cache[cache_key][1] < self.CACHE_EXPIRY:
            return self.cache[cache_key][0]

        headers = {"auth-token": self.api_key}
        co2_data = None
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL, headers=headers, params=params) as response:
                data = await response.json()
                co2_data = self._process_co2_data(data)
        
        # Store the data and the current time in the cache
        self.cache[cache_key] = (co2_data, datetime.now(timezone.utc))
        self._save_cache()  # Save the cache to the file

        return co2_data

    def _process_co2_data(self, data):
        data_updated_at = datetime.strptime(data["updatedAt"], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
        #verify its within the last minutes defined by co2_time_threshold
        if abs((data_updated_at - datetime.now(timezone.utc)).total_seconds()) / 60 > self.co2_time_threshold_mins:
            return None
        return float(data["carbonIntensity"])


   