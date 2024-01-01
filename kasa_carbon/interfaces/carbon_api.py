from abc import ABC, abstractmethod

class CarbonAPI(ABC):
    @abstractmethod
    async def get_co2_by_latlon(self, lat: float, lon: float) -> float:
        """
        Get the current CO2 emission rate per kWh for a specific location, identified by latitude and longitude.

        :param lat: The latitude of the location.
        :param lon: The longitude of the location.
        :return: The current CO2 emission rate per kWh.
        """
        pass

    @abstractmethod
    async def get_co2_by_gridid(self, grid_id: str) -> float:
        """
        Get the current CO2 emission rate per kWh for a specific location, identified by grid ID.

        :param grid_id: The ID of the grid.
        :return: The current CO2 emission rate per kWh.
        """
        pass