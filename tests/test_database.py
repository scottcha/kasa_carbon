# FILEPATH: /C:/Users/scott/source/repos/kasa_carbon/tests/test_database.py

import pytest
import asyncpg
from unittest.mock import patch, AsyncMock, Mock
from modules.database import Database
import config
   

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
async def test_write_usage(energy_usage):
    # Arrange
    db_config = {"user": "test", "password": "test", "database": "test", "host": "localhost"}
    db = Database(db_config)

    with patch('asyncpg.connect', new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value.execute = AsyncMock()
        mock_connect.return_value.is_closed = Mock(return_value=False)
        mock_connect.return_value.close = AsyncMock()

        # Act
        await db.write_usage(energy_usage)
        
        # Assert
        mock_connect.assert_called_once_with(**db_config)
        expected_query = db._generate_insert_sql_query(energy_usage)
        mock_connect.return_value.execute.assert_called_once_with(
            expected_query,
            *energy_usage.values()
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
    expected_query = db._generate_select_sql_query()
    mock_connect.return_value.fetch.assert_called_once_with(expected_query)
    mock_connect.return_value.close.assert_called_once()

@pytest.mark.asyncio
@pytest.mark.real_database
async def test_write_usage_realdb(energy_usage):
    # Arrange
    db_config = config.db_config
    db = Database(db_config)

    # Act
    await db.write_usage(energy_usage)

    # Assert
    conn = await asyncpg.connect(**db_config)
    try:
        result = await conn.fetchrow("SELECT * FROM energy_usage WHERE device = $1", energy_usage["device"])
        assert result is not None
        for key, value in energy_usage.items():
            assert result[key] == value
        
    finally:
        await conn.execute("DELETE FROM energy_usage")
        await conn.close()

@pytest.mark.asyncio
@pytest.mark.real_database
async def test_read_usage_realdb(energy_usage):
    # Arrange
    db_config = config.db_config 
    db = Database(db_config)
  
    conn = await asyncpg.connect(**db_config)
    try:
        insert_query = db._generate_insert_sql_query(energy_usage)
        await conn.execute(insert_query, *energy_usage.values())
    finally:
        await conn.close()

    # Act
    result = await db.read_usage()

    # Assert
    assert len(result) > 0
    for key, value in energy_usage.items():
        assert result[0][key] == value

    conn = await asyncpg.connect(**db_config)
    try:
        await conn.execute("DELETE FROM energy_usage")
    finally:
        await conn.close()