from datetime import datetime, timedelta, timezone
import pytest
from kasa_carbon.modules.device_factory import create_monitor
from kasa_carbon.modules.omada_monitor import OmadaMonitor

@pytest.fixture
def omada_monitor():
    api_key = "test_api_key"
    local_lat = 40.7128
    local_lon = -74.0060
    monitor = create_monitor('omada', api_key=api_key, local_lat=local_lat, local_lon=local_lon, local_grid_id="DE")
    return monitor

@pytest.mark.real_device
def test_get_new_tokens(omada_monitor):
    omada_monitor.get_new_tokens()
    assert omada_monitor.token is not None
    assert omada_monitor.refresh_token is not None
    assert omada_monitor.token_expiration > datetime.now(timezone.utc)
    assert omada_monitor.refresh_token_expiration > datetime.now(timezone.utc)

@pytest.mark.real_device
def test_refresh_access_token(omada_monitor):
    omada_monitor.get_new_tokens()  # Ensure we have initial tokens
    omada_monitor.refresh_access_token()
    assert omada_monitor.token is not None
    assert omada_monitor.token_expiration > datetime.now(timezone.utc)

@pytest.mark.real_device
def test_get_api_headers_with_valid_token(omada_monitor):
    omada_monitor.get_new_tokens()  # Ensure we have a valid token
    headers = omada_monitor.get_api_headers()
    assert headers['Authorization'] == f"AccessToken={omada_monitor.token}"
    assert headers['Content-Type'] == "application/json"

@pytest.mark.real_device
def test_get_api_headers_with_expired_token(omada_monitor):
    omada_monitor.get_new_tokens()  # Ensure we have initial tokens
    omada_monitor.token_expiration = datetime.now(timezone.utc) - timedelta(hours=1)  # Expire the token
    headers = omada_monitor.get_api_headers()
    assert headers['Authorization'] == f"AccessToken={omada_monitor.token}"
    assert headers['Content-Type'] == "application/json"

@pytest.mark.real_device
def test_get_api_headers_with_expired_refresh_token(omada_monitor):
    omada_monitor.get_new_tokens()  # Ensure we have initial tokens
    omada_monitor.token_expiration = datetime.now(timezone.utc) - timedelta(hours=1)  # Expire the token
    omada_monitor.refresh_token_expiration = datetime.now(timezone.utc) - timedelta(days=1)  # Expire the refresh token
    headers = omada_monitor.get_api_headers()
    assert headers['Authorization'] == f"AccessToken={omada_monitor.token}"
    assert headers['Content-Type'] == "application/json"

def test_parse_energy_data():
    data = {
        'errorCode': 0,
        'msg': 'Success.',
        'result': [{
            'mac': '98-25-4A-F8-FC-3B',
            'name': '98-25-4A-F8-FC-3B',
            'portNum': 24,
            'totalPowerUsed': 6,
            'totalPercentUsed': 1.1,
            'totalPower': 500,
            'poePorts': [
                {'portId': 1, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 2, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 3, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 4, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 5, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 6, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 7, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 8, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 9, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 10, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 11, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 12, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 13, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 14, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 15, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 16, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 17, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 18, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 19, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 20, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 21, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 22, 'poeSupported': True, 'poeEnabled': False},
                {'portId': 23, 'poeSupported': True, 'poeEnabled': True, 'poePower': 0, 'poePercent': 0},
                {'portId': 24, 'poeSupported': True, 'poeEnabled': True, 'poePower': 4, 'poePercent': 6},
                {'portId': 25, 'poeSupported': False},
                {'portId': 26, 'poeSupported': False},
                {'portId': 27, 'poeSupported': False},
                {'portId': 28, 'poeSupported': False}
            ]
        }]
    }
    
    expected_output = {
        '23': 0,
        '24': 4
    }
    
    actual_output = OmadaMonitor._parse_energy_data(data)
    assert actual_output == expected_output   