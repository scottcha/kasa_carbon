from abc import ABC, abstractmethod
from modules.energy_usage import EnergyUsage

class DatastoreAPI(ABC):
    @abstractmethod
    async def write_usage(self, energy_usage: EnergyUsage) -> None:
        pass

    @abstractmethod
    async def read_usage(self, columns="*"):
        pass

    @abstractmethod
    async def close(self):
        pass