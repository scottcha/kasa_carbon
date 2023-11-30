import asyncio
import asyncpg

class Database:
    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = None

    async def write_usage(self, energy_usage):
        self.conn = await asyncpg.connect(**self.db_config)
        try:
            await self.conn.execute(
                "INSERT INTO energy_usage (device, timestamp, power, avg_mg_co2) VALUES ($1, $2, $3, $4)",
                energy_usage["device"], energy_usage["timestamp"], energy_usage["power"], energy_usage["avg_mg_co2"]
            )
        finally:
            await self.close()

    async def read_usage(self):
        self.conn = await asyncpg.connect(**self.db_config)
        try:
            result = await self.conn.fetch("SELECT * FROM energy_usage")
        finally:
            await self.close()
        return result

    async def close(self):
        if self.conn is not None and not self.conn.is_closed():
            await self.conn.close()
            self.conn = None