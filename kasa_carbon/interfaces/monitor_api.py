from abc import ABC, abstractmethod
from kasa_carbon.interfaces.datastore_api import DatastoreAPI

class MonitorAPI(ABC):
    @abstractmethod
    def __init__(self, api_key, local_lat=None, local_lon=None, local_grid_id=None, co2_api_provider="ElectricityMaps", em_cache_expiry_mins=30):
        pass

    @abstractmethod
    async def discover_devices(self):
        pass
    
    @abstractmethod
    async def monitor_energy_use_once(self):
        pass
    
    @abstractmethod
    async def monitor_energy_use_continuously(self, db: DatastoreAPI, delay: int, timeout: int=None):
        pass
