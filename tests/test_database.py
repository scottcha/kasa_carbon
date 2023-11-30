# FILEPATH: /C:/Users/scott/source/repos/kasa_carbon/tests/test_database.py

import pytest
import asyncpg
from unittest.mock import patch, AsyncMock, Mock
from modules.database import Database
import config
from datetime import datetime, timezone
import pytz

@pytest.fixture(autouse=True)
@pytest.mark.real_database
async def setup_method():
    # Your setup code here
    db_config = config.db_config
    conn = await asyncpg.connect(**db_config)
    await conn.execute("DELETE FROM energy_usage")
    await conn.close()
   
    yield  # This is where the test will run
    
    db_config = config.db_config
    conn = await asyncpg.connect(**db_config)
    await conn.execute("DELETE FROM energy_usage")
    await conn.close()
    print("Tearing down")

@pytest.mark.asyncio
async def test_write_usage():
    # Arrange
    db_config = {"user": "test", "password": "test", "database": "test", "host": "localhost"}
    db = Database(db_config)
    energy_usage = {"device": "test_device", "timestamp": "2022-01-01 00:00:00", "power": 100, "avg_mg_co2": 50}

    with patch('asyncpg.connect', new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value.execute = AsyncMock()
        mock_connect.return_value.is_closed = Mock(return_value=False)
        mock_connect.return_value.close = AsyncMock()

        # Act
        await db.write_usage(energy_usage)
        
        # Assert
        mock_connect.assert_called_once_with(**db_config)
        mock_connect.return_value.execute.assert_called_once_with(
            "INSERT INTO energy_usage (device, timestamp, power, avg_mg_co2) VALUES ($1, $2, $3, $4)",
            energy_usage["device"], energy_usage["timestamp"], energy_usage["power"], energy_usage["avg_mg_co2"]
        )
        mock_connect.return_value.close.assert_called_once()

@pytest.mark.asyncio
async def test_read_usage():
    # Arrange
    db_config = {"user": "test", "password": "test", "database": "test", "host": "localhost"}
    db = Database(db_config)

    # Act
    with patch('asyncpg.connect', new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value.fetch = AsyncMock()
        mock_connect.return_value.is_closed = Mock(return_value=False)
        mock_connect.return_value.close = AsyncMock()
        await db.read_usage()

    # Assert
    mock_connect.assert_called_once_with(**db_config)
    mock_connect.return_value.fetch.assert_called_once_with("SELECT * FROM energy_usage")
    mock_connect.return_value.close.assert_called_once() 

@pytest.mark.asyncio
@pytest.mark.real_database
async def test_write_usage_realdb():
    # Arrange
    db_config = config.db_config
    db = Database(db_config)
    timestamp_str = "2022-01-01 00:00:00"
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    timestamp = pytz.utc.localize(timestamp)  # Make timestamp timezone aware and in UTC timezone
    energy_usage = {"device": "test_device", "timestamp": timestamp, "power": 100.0, "avg_mg_co2": 50.0}

    # Act
    await db.write_usage(energy_usage)

    # Assert
    conn = await asyncpg.connect(**db_config)
    try:
        result = await conn.fetchrow("SELECT * FROM energy_usage WHERE device = $1", energy_usage["device"])
        assert result is not None
        assert result["device"] == energy_usage["device"]
        assert result["timestamp"] == energy_usage["timestamp"]
        assert result["power"] == energy_usage["power"]
        assert result["avg_mg_co2"] == energy_usage["avg_mg_co2"]
    finally:
        await conn.execute("DELETE FROM energy_usage")
        await conn.close()

@pytest.mark.asyncio
@pytest.mark.real_database
async def test_read_usage_realdb():
    # Arrange
    db_config = config.db_config 
    db = Database(db_config)
    timestamp_str = "2022-01-01 00:00:00"
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    timestamp = pytz.utc.localize(timestamp)  # Make timestamp timezone aware and in UTC timezone
    energy_usage = {"device": "test_device", "timestamp": timestamp, "power": 100.0, "avg_mg_co2": 50.0}

    conn = await asyncpg.connect(**db_config)
    try:
        await conn.execute(
            "INSERT INTO energy_usage (device, timestamp, power, avg_mg_co2) VALUES ($1, $2, $3, $4)",
            energy_usage["device"], energy_usage["timestamp"], energy_usage["power"], energy_usage["avg_mg_co2"]
        )
    finally:
        await conn.close()

    # Act
    result = await db.read_usage()

    # Assert
    assert len(result) > 0
    assert result[0]["device"] == energy_usage["device"]
    # Convert the original timestamp to the client's timezone
    timestamp_client_tz = energy_usage["timestamp"].astimezone(timezone.utc)
    assert result[0]["timestamp"] == timestamp_client_tz
    assert result[0]["power"] == energy_usage["power"]
    assert result[0]["avg_mg_co2"] == energy_usage["avg_mg_co2"]

    conn = await asyncpg.connect(**db_config)
    try:
        await conn.execute("DELETE FROM energy_usage")
    finally:
        await conn.close()