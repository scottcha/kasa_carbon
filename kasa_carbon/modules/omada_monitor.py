from kasa_carbon.modules.database import Database
from kasa_carbon.interfaces.datastore_api import DatastoreAPI
from kasa_carbon.modules.electricitymaps_api import ElectricityMapAPI
from kasa_carbon.modules.energy_usage import EnergyUsage
from kasa_carbon.interfaces.monitor_api import MonitorAPI
import time
from datetime import datetime, timedelta, timezone
import os
import requests
import json
from dotenv import load_dotenv

# Ignore SSL certificate errors
import urllib3

from kasa_carbon.modules.generic_monitor import monitor_energy_use
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OmadaMonitor(MonitorAPI):
    def __init__(self, api_key, local_lat=None, local_lon=None, local_grid_id=None, co2_api_provider="ElectricityMaps", em_cache_expiry_mins=30):
        self.devices = []
        self.lat = local_lat 
        self.lon = local_lon 
        self.grid_id = None
        if (local_lat is None or local_lon is None) and local_grid_id is None:
            raise ValueError("Must provide either local_lat/local_lon or local_grid_id")
        elif local_grid_id is not None:
            self.grid_id = local_grid_id
        #else should be just use local_lat/local_lon

        if co2_api_provider == "ElectricityMaps":
            self.co2_api = ElectricityMapAPI(em_api_key=api_key, em_cache_expiry_mins=em_cache_expiry_mins)
        else:
            raise ValueError("co2_api_provider must be 'EM' until others are supported")
        
        load_dotenv()
        self.client_id = os.getenv('OMADA_CLIENT_ID')
        self.client_secret = os.getenv('OMADA_CLIENT_SECRET')
        self.omadac_id = os.getenv('OMADA_OMADAC_ID')
        self.omada_base_url = os.getenv('OMADA_BASE_URL')
        self.token = None
        self.refresh_token = None
        self.token_expiration = None
        self.refresh_token_expiration = None 
        self.site_id = None

    
    def get_api_headers(self):
        if self.token is None or datetime.now(timezone.utc) >= self.token_expiration:
            if self.refresh_token and datetime.now(timezone.utc) < self.refresh_token_expiration:
                self.refresh_access_token()
            else:
                self.get_new_tokens()

        return {
            "Authorization": f"AccessToken={self.token}",
            "Content-Type": "application/json"
        }

    def get_new_tokens(self):
        headers = {
            "Content-Type": "application/json"
        }

        body = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "omadacId": self.omadac_id
        }

        response = requests.post(
            f"{self.omada_base_url}/openapi/authorize/token?grant_type=client_credentials",
            headers=headers,
            data=json.dumps(body),
            verify=False  # Ignore SSL certificate errors
        )

        if response.status_code != 200:
            print(f"Failed to get access token: {response.status_code} - {response.text}")
            exit()

        result = response.json()['result']
        self.token = result['accessToken']
        self.refresh_token = result['refreshToken']
        token_expiration = result['expiresIn']
        self.token_expiration = datetime.now(timezone.utc) + timedelta(seconds=token_expiration)
        self.refresh_token_expiration = datetime.now(timezone.utc) + timedelta(days=13) #actually 14 but providing a buffer

    def refresh_access_token(self):
        headers = {
            "Content-Type": "application/json"
        }

        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        }

        response = requests.post(
            f"{self.omada_base_url}/openapi/authorize/token?grant_type=refresh_token",
            headers=headers,
            params=params,
            verify=False  # Ignore SSL certificate errors
        )

        if response.status_code != 200:
            print(f"Failed to refresh access token: {response.status_code} - {response.text}")
            self.get_new_tokens()
            return

        result = response.json()['result']
        self.token = result['accessToken']
        token_expiration = result['expiresIn']
        self.token_expiration = datetime.now(timezone.utc) + timedelta(seconds=token_expiration)
    
    def get_site_id(self):
        if self.site_id is None:
            api_headers = self.get_api_headers()
            site_response = requests.get(
                f"{self.omada_base_url}/openapi/v1/{self.omadac_id}/sites?pageSize=1&page=1",
                headers=api_headers,
                verify=False  # Ignore SSL certificate errors
            )

            if site_response.status_code != 200:
                #throw exception
                raise Exception(f"Failed to get site: {site_response.status_code} - {site_response.text}")

            self.site_id = site_response.json()['result']['data'][0]['siteId']
        return self.site_id
                  
    async def discover_devices(self):
        #not needed for omada
        pass
    
    def _parse_energy_data(data):
        energy_data = {}
        for device in data['result']:
            for port in device['poePorts']:
                if port.get('poeEnabled', False):
                    energy_data[str(port['portId'])] = port.get('poePower', 0)
        return energy_data 
    
    async def monitor_energy_use_once(self):
        api_headers = self.get_api_headers()
        site_id = self.get_site_id()
        poe_response = requests.get(
            f"{self.omada_base_url}/openapi/v1/{self.omadac_id}/sites/{site_id}/dashboard/poe-usage?pageSize=1&page=1",
            headers=api_headers,
            verify=False  # Ignore SSL certificate errors
        )
        if poe_response.status_code != 200:
            #throw exception 
            raise Exception(f"Failed to get POE utilization: {poe_response.status_code} - {poe_response.text}")

        poe_data = poe_response.json()
        energy_values = OmadaMonitor._parse_energy_data(poe_data) 
        
        return energy_values
    
    #get carbon data by either grid or lat/lon
    async def _get_co2_data(self):
        if self.grid_id is not None:
            return await self.co2_api.get_co2_by_gridid(self.grid_id)
        else:
            return await self.co2_api.get_co2_by_latlon(self.lat, self.lon)  
    
    async def monitor_energy_use_continuously(self, db, delay=5, timeout=60):
        await monitor_energy_use(self.monitor_energy_use_once, self._get_co2_data, db, delay, timeout)