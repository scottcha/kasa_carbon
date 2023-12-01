import pytest
from unittest.mock import patch, AsyncMock
from modules.electricitymaps_api import ElectricityMapAPI
from datetime import datetime, timedelta, timezone
import math


@pytest.mark.asyncio
@pytest.mark.real_em_api
async def test_get_co2_by_gridid_real_em_api():
    # Arrange
    api = ElectricityMapAPI(clear_cache=True)
    grid_id = "DE"  

    # Act
    result = await api.get_co2_by_gridid(grid_id)

    # Assert
    assert isinstance(result, float)  # The result should be a float

@pytest.mark.asyncio
@pytest.mark.real_em_api
async def test_get_co2_by_latlon_real_em_api():
    # Arrange
    api = ElectricityMapAPI(clear_cache=True)
    lat, lon = 51.509865, -0.118092  

    # Act
    result = await api.get_co2_by_latlon(lat, lon)

    # Assert
    assert isinstance(result, float)  # The result should be a float

@pytest.mark.asyncio
@pytest.mark.real_em_api
async def test_get_co2_by_gridid_uses_cache():
    # Arrange
    api = ElectricityMapAPI(clear_cache=True)
    grid_id = "DE"

    # Act
    result1 = await api.get_co2_by_gridid(grid_id)
    result2 = await api.get_co2_by_gridid(grid_id)

    # Assert
    assert result1 == result2  # The results should be the same