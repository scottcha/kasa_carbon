import pytest
import os
from unittest.mock import MagicMock, AsyncMock, Mock, patch
from kasa_carbon.modules.kasa_monitor import KasaMonitor
from kasa_carbon.modules.omada_monitor import OmadaMonitor
from kasa_carbon.modules.database import Database
from kasa_carbon.modules.electricitymaps_api import ElectricityMapAPI  # Assuming this is the correct import
from kasa_carbon.modules.device_factory import create_monitor
import asyncpg

@pytest.mark.parametrize("monitor_type", ["kasa", "omada"])
def test_init_with_lat_lon(monitor_type):
    # Arrange
    api_key = "test_api_key"
    local_lat = 40.7128
    local_lon = -74.0060

    # Act
    #kasa = KasaMonitor(api_key=api_key, local_lat=local_lat, local_lon=local_lon)
    monitor = create_monitor(monitor_type, api_key=api_key, local_lat=local_lat, local_lon=local_lon)

    # Assert
    assert monitor.lat == local_lat
    assert monitor.lon == local_lon
    assert monitor.grid_id is None
    assert isinstance(monitor.co2_api, ElectricityMapAPI)

@pytest.mark.parametrize("monitor_type", ["kasa", "omada"])
def test_init_with_grid_id(monitor_type):
    # Arrange
    api_key = "test_api_key"
    local_grid_id = "test_grid_id"

    # Act
    monitor = create_monitor(monitor_type, api_key=api_key, local_grid_id=local_grid_id)

    # Assert
    assert monitor.lat is None
    assert monitor.lon is None
    assert monitor.grid_id == local_grid_id
    assert isinstance(monitor.co2_api, ElectricityMapAPI)

@pytest.mark.parametrize("monitor_type", ["kasa", "omada"])
def test_init_missing_lat_lon_and_grid_id(monitor_type):
    # Arrange
    api_key = "test_api_key"

    # Act & Assert
    with pytest.raises(ValueError, match="Must provide either local_lat/local_lon or local_grid_id"):
        create_monitor(monitor_type, api_key=api_key)

@pytest.mark.parametrize("monitor_type", ["kasa", "omada"])
def test_init_invalid_co2_api_provider(monitor_type):
    # Arrange
    api_key = "test_api_key"
    local_lat = 40.7128
    local_lon = -74.0060

    # Act & Assert
    with pytest.raises(ValueError, match="co2_api_provider must be 'EM' until others are supported"):
        create_monitor(monitor_type, api_key=api_key, local_lat=local_lat, local_lon=local_lon, co2_api_provider="InvalidProvider")

@pytest.mark.asyncio
@pytest.mark.parametrize("monitor_type", ["kasa"])
async def test_discover_devices(monitor_type):
    # Arrange
    with patch('kasa.Discover.discover') as mock_discover:
        mock_discover.return_value = {}
        monitor = create_monitor(monitor_type, api_key=None, local_lat=None, local_lon=None, local_grid_id="DE")

        # Act
        await monitor.discover_devices()

        # Assert
        mock_discover.assert_called_once()

@pytest.mark.asyncio
async def test_monitor_kasa_energy_use():
    # Arrange
    with patch('kasa.Discover.discover') as mock_discover:
        mock_device = AsyncMock()
        mock_device.has_emeter = True
        mock_device.alias = "Device"
        mock_device.emeter_realtime = {"power": 100}
        mock_discover.return_value = {"192.168.0.1": mock_device}
        kasa = KasaMonitor(api_key=None, local_lat=None, local_lon=None, local_grid_id="DE")
        await kasa.discover_devices()

        # Act
        energy_values = await kasa.monitor_energy_use_once()

        # Assert
        assert energy_values == {"Device": 100}


@pytest.mark.asyncio
@pytest.mark.real_device
@pytest.mark.parametrize("monitor_type", ["kasa"])
async def test_connect_to_real_device(monitor_type):
    # Arrange
    monitor = create_monitor(monitor_type, api_key=None, local_lat=None, local_lon=None, local_grid_id="DE")

    # Act
    if monitor_type == "kasa":
        await monitor.discover_devices()

    # Assert
    assert len(monitor.devices) > 0, f"No {monitor_type.capitalize()} devices found on the network"

@pytest.mark.asyncio
@pytest.mark.real_device
@pytest.mark.parametrize("monitor_type", ["kasa", "omada"])
async def test_monitor_energy_use_real_device(monitor_type):
    # Arrange
    monitor = create_monitor(monitor_type, api_key=None, local_lat=None, local_lon=None, local_grid_id="DE")
    await monitor.discover_devices()

    # Act
    energy_values = await monitor.monitor_energy_use_once()

    # Assert
    assert energy_values, f"No energy values were returned for {monitor_type.capitalize()} devices"

@pytest.mark.asyncio
@pytest.mark.real_device
@pytest.mark.real_database
@pytest.mark.parametrize("monitor_type", ["kasa", "omada"])
async def test_monitor_energy_use_continuously_integration(monitor_type, energy_usage_test_data):
    # Arrange
    db_config = {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
    }
    local_lat = float(os.getenv("LOCAL_LAT"))
    local_lon = float(os.getenv("LOCAL_LON"))
    em_api_key = os.getenv("EM_API_KEY")
    db = Database(db_config)
    monitor = create_monitor(monitor_type, api_key=em_api_key, local_lat=local_lat, local_lon=local_lon)

    await monitor.discover_devices()

    # Act
    # This will run the method for 60 seconds and then stop
    await monitor.monitor_energy_use_continuously(db, delay=5, timeout=20)

    # Assert
    # Check the database to ensure that the energy usage data was written correctly
    result = await db.read_usage()

    assert len(result) > 0
    for key, value in energy_usage_test_data.get_dict().items():
        assert result[0][key] is not None 

    # Empty the db again    
    conn = await asyncpg.connect(**db_config)
    try:
        await conn.execute("DELETE FROM energy_usage")
    finally:
        await conn.close()