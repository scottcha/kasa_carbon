from datetime import datetime, timezone

class EnergyUsage:
    def __init__(self, device=None, power=None, co2emitted=None, co2=None, energy_usage_dict=None):
        if energy_usage_dict is not None:
            self.device = energy_usage_dict["device"]
            self.timestamp = energy_usage_dict["timestamp"]
            self.power_draw_watts = energy_usage_dict["power_draw_watts"]
            self.avg_emitted_mgco2e = energy_usage_dict["avg_emitted_mgco2e"]
            self.grid_carbon_intensity_gco2perkwhr = energy_usage_dict["grid_carbon_intensity_gco2perkwhr"]
        else:
            self.device = device
            self.timestamp = datetime.now(timezone.utc)
            self.power_draw_watts = power
            self.avg_emitted_mgco2e = co2emitted
            self.grid_carbon_intensity_gco2perkwhr = co2
    
    #get dict representation of energy usage
    def get_dict(self) -> dict:
        return {"device": self.device, "timestamp": self.timestamp, "power_draw_watts": self.power_draw_watts, 
                "avg_emitted_mgco2e": self.avg_emitted_mgco2e, "grid_carbon_intensity_gco2perkwhr": self.grid_carbon_intensity_gco2perkwhr}
    
    #get csv headers
    @staticmethod
    def keys() -> list:
        return ["device", "timestamp", "power_draw_watts", "avg_emitted_mgco2e", "grid_carbon_intensity_gco2perkwhr"]