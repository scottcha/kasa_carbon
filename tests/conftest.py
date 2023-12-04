import pytest
import re
from datetime import datetime, timezone
import pytz
from modules.energy_usage import EnergyUsage

@pytest.fixture
def energy_usage_test_data() -> EnergyUsage:
    # Read the SQL file
    with open('sql/01_init.sql', 'r') as file:
        sql = file.read()

    # Parse the CREATE TABLE statement to get the column names and types
    match = re.search(r'CREATE TABLE IF NOT EXISTS energy_usage \((.*)\)\s*;', sql, re.DOTALL)
    column_definitions = re.split(r',(?![^(]*\))', match.group(1))
    columns = [re.search(r'^\s*(\w+)\s+(.+)', column_definition).groups() for column_definition in column_definitions]

    # Create the energy_usage dictionary with test values based on the column names and types
    energy_usage = {}
    for column_name, column_type in columns:
        if 'VARCHAR' in column_type:
            energy_usage[column_name] = 'test_value'
        elif 'TIMESTAMPTZ' in column_type:
            timestamp_str = "2022-01-01 00:00:00"
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            timestamp = pytz.utc.localize(timestamp)  # Make timestamp timezone aware and in UTC timezone
            energy_usage[column_name] = timestamp 
        elif 'integer' in column_type:
            energy_usage[column_name] = 100
        elif 'real' in column_type:
            energy_usage[column_name] = 50.0
 
    return EnergyUsage(energy_usage_dict=energy_usage)