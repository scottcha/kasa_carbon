import time
from datetime import datetime, timezone
from kasa_carbon.modules.energy_usage import EnergyUsage

async def monitor_energy_use(get_energy_values, get_co2_data, db, delay, timeout=None):
	start_time = time.time()

	try:
		while True:
			energy_values = await get_energy_values()

			# Get average CO2 from API
			co2 = await get_co2_data()
			for device, power in energy_values.items():
				# Convert grid CO2 to device actual CO2 by taking the timespan (assuming constant power draw over that period) and 
				# multiplying by the grid CO2 while also converting to mgCO2e
				power_kwatts = power / 1000.0  # Convert to kW from watts
				hours = delay / 3600.0  # Time in use in hours
				co2emitted = hours * power_kwatts * co2 / 1000.0  # Convert to mgCO2e 
				energy_usage = {
					"device": device, 
					"timestamp": datetime.now(timezone.utc), 
					"power_draw_watts": power, 
					"avg_emitted_mgco2e": co2emitted,
					"grid_carbon_intensity_gco2perkwhr": co2
				}

				await db.write_usage(EnergyUsage(energy_usage_dict=energy_usage))

			if timeout is not None and time.time() - start_time >= timeout:
				break

			time.sleep(delay)
	finally:
		await db.close()