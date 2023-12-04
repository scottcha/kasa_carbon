import pytest
from unittest.mock import MagicMock, AsyncMock, Mock, patch
from modules.kasa_monitor import KasaMonitor
from modules.database import Database
import config
import asyncpg

@pytest.mark.asyncio
async def test_discover_devices():
    # Arrange
    with patch('kasa.Discover.discover') as mock_discover:
        mock_discover.return_value = {}
        kasa = KasaMonitor()

        # Act
        await kasa.discover_devices()

        # Assert
        mock_discover.assert_called_once()

@pytest.mark.asyncio
async def test_monitor_energy_use():
    # Arrange
    with patch('kasa.Discover.discover') as mock_discover:
        mock_device = AsyncMock()
        mock_device.has_emeter = True
        mock_device.alias = "Device"
        mock_device.emeter_realtime = {"power": 100}
        mock_discover.return_value = {"192.168.0.1": mock_device}
        kasa = KasaMonitor()
        await kasa.discover_devices()

        # Act
        energy_values = await kasa.monitor_energy_use_once()

        # Assert
        assert energy_values == {"Device": 100}


@pytest.mark.asyncio
@pytest.mark.real_device
async def test_connect_to_real_device():
    # Arrange
    kasa = KasaMonitor()

    # Act
    await kasa.discover_devices()

    # Assert
    assert len(kasa.devices) > 0, "No Kasa devices found on the network"

@pytest.mark.asyncio
@pytest.mark.real_device
async def test_monitor_energy_use_real_device():
    # Arrange
    kasa = KasaMonitor()
    await kasa.discover_devices()

    # Act
    energy_values = await kasa.monitor_energy_use_once()

    # Assert
    assert energy_values, "No energy values were returned"

@pytest.mark.asyncio
@pytest.mark.real_device
@pytest.mark.real_database
async def test_monitor_energy_use_continuously_integration(energy_usage_test_data):
    # Arrange
    db_config = config.db_config
    db = Database(db_config)
    monitor = KasaMonitor()

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


    #empty the db again    
    conn = await asyncpg.connect(**db_config)
    try:
        await conn.execute("DELETE FROM energy_usage")
    finally:
        await conn.close()