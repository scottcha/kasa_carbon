import asyncio
import pytest
from unittest.mock import patch, mock_open, call
from modules.file_storage import FileStorage
from modules.energy_usage import EnergyUsage
import os

@pytest.mark.asyncio
async def test_read_usage():
    # Arrange
    file_path = "/path/to/your/file"
    mock_file_content = ["device,timestamp,power_draw_watts,avg_emitted_mgco2e,grid_carbon_intensity_gco2perkwhr\n",
                         "device1,2022-01-01T00:00:00Z,100,200,300\n",
                         "device2,2022-01-01T00:00:01Z,110,210,310\n"]

    # Act
    with patch("builtins.open", mock_open(read_data="".join(mock_file_content))) as mock_file, \
         patch("os.path.isfile", return_value=True):
        file_storage = FileStorage(file_path, "append")
        result = await file_storage.read_usage()

    # Assert
    mock_file.assert_called_once_with(file_path, 'r')
    assert result == mock_file_content

@pytest.mark.asyncio
async def test_write_usage_append_mode():
    # Arrange
    file_path = "/path/to/your/file"
    energy_usage = EnergyUsage("device1", 100, 200, 300)
    mock_file_content = ["device,timestamp,power_draw_watts,avg_emitted_mgco2e,grid_carbon_intensity_gco2perkwhr\n",
                         "device1,2022-01-01T00:00:00Z,100,200,300\n"]

    # Act
    with patch("builtins.open", mock_open()) as mock_file, \
         patch("os.path.isfile", return_value=True):
        file_storage = FileStorage(file_path, "append")
        await file_storage.write_usage(energy_usage)

    # Assert
    mock_file.assert_called_once_with(file_path, 'a', newline='')
    mock_file().write.assert_called_once_with(','.join(map(str, energy_usage.get_dict().values())) + '\r\n')

@pytest.mark.asyncio
async def test_write_usage_overwrite_mode():
    # Arrange
    file_path = "/path/to/your/file"
    energy_usage = EnergyUsage("device1", 100, 200, 300)
    mock_file_content = ["device,timestamp,power_draw_watts,avg_emitted_mgco2e,grid_carbon_intensity_gco2perkwhr\n",
                         "device1,2022-01-01T00:00:00Z,100,200,300\n"]

    # Act
    with patch("builtins.open", mock_open()) as mock_file, \
         patch("os.path.isfile", return_value=True):
        file_storage = FileStorage(file_path, "overwrite")
        await file_storage.write_usage(energy_usage)

    # Assert
    mock_file.assert_called_once_with(file_path, 'w',  newline='')
    mock_file().write.assert_called_once_with(','.join(map(str, energy_usage.get_dict().values())) + '\r\n')