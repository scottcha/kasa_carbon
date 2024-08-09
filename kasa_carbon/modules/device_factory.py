from kasa_carbon.modules.omada_monitor import OmadaMonitor
from kasa_carbon.modules.kasa_monitor import KasaMonitor

def create_monitor(device_type, **kwargs):
	"""
	Factory function to create a monitor instance based on device type.

	Args:
		device_type (str): The type of device monitor to create ('omada' or 'kasa').
		**kwargs: Additional keyword arguments to pass to the monitor class.

	Returns:
		An instance of OmadaMonitor or KasaMonitor.

	Raises:
		ValueError: If the device_type is not recognized.
	"""
	if device_type == 'omada':
		return OmadaMonitor(**kwargs)
	elif device_type == 'kasa':
		return KasaMonitor(**kwargs)
	else:
		raise ValueError(f"Unknown device_type: {device_type}")

# Example usage:
# monitor = create_monitor('omada', api_key='your_api_key', local_lat=40.7128, local_lon=-74.0060)
# monitor = create_monitor('kasa', api_key='your_api_key', local_grid_id='your_grid_id')