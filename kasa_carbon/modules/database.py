import asyncio
import asyncpg
from kasa_carbon.modules.energy_usage import EnergyUsage
from kasa_carbon.interfaces.datastore_api import DatastoreAPI

class Database(DatastoreAPI):
    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = None

    async def write_usage(self, energy_usage: EnergyUsage) -> None:
        self.conn = await asyncpg.connect(**self.db_config)
        try:
            energy_usage_dict = energy_usage.get_dict()
            sql_query = self._generate_insert_sql_query(energy_usage)
            await self.conn.execute(sql_query, *energy_usage_dict.values())
        finally:
            await self.close()

    async def read_usage(self, last_n=10, columns="*"):
        self.conn = await asyncpg.connect(**self.db_config)
        try:
            sql_query = self._generate_select_sql_query(last_n, columns=columns)
            result = await self.conn.fetch(sql_query)
        finally:
            await self.close()
        return result

    async def close(self):
        if self.conn is not None and not self.conn.is_closed():
            await self.conn.close()
            self.conn = None

    def _generate_insert_sql_query(self, energy_usage: EnergyUsage):
        energy_usage_dict = energy_usage.get_dict()
        columns = ', '.join(energy_usage_dict.keys())
        values = ', '.join(['$' + str(i) for i in range(1, len(energy_usage_dict) + 1)])
        return f"INSERT INTO energy_usage ({columns}) VALUES ({values})"

    def _generate_select_sql_query(self, last_n, columns="*"):
        if columns == "*":
            columns_str = "*"
        else:
            columns_str = ', '.join(columns)
        return f"SELECT {columns_str} FROM energy_usage ORDER BY timestamp DESC LIMIT {last_n}"