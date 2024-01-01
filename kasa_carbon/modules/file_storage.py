import asyncio
from kasa_carbon.modules.energy_usage import EnergyUsage
from kasa_carbon.interfaces.datastore_api import DatastoreAPI
import csv, os

class FileStorage(DatastoreAPI): 
    def __init__(self, file_path, storage_mode="append"):
        self.file_path = file_path
        self.storage_mode = storage_mode

        #create file if it doesn't exist & write headers
        file_exists = os.path.isfile(self.file_path)
        if not file_exists:
            with open(self.file_path, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(EnergyUsage.keys())

    async def write_usage(self, energy_usage: EnergyUsage) -> None:
        mode = 'a' if self.storage_mode == 'append' else 'w'
        with open(self.file_path, mode, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(energy_usage.get_dict().values())

    async def read_usage(self, last_n=10, columns="*"):
        with open(self.file_path, 'r') as f:
            #read last_n lines
            lines = f.readlines()[-last_n:]
            return lines 

    async def close(self):
        pass