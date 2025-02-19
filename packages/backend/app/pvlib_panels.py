import requests
import json
import pandas as pd
import pvlib
from pvlib import location, modelchain, pvsystem, temperature
import matplotlib.pyplot as plt

### 1️⃣ Fetch Weather Data from NWS ###
def get_weather_data(lat, lon):
    point_response = requests.get(f'https://api.weather.gov/points/{lat},{lon}')
    point_data = point_response.json()
    
    forecast_url = point_data['properties']['forecast']
    response = requests.get(forecast_url)
    forecast_data = response.json()

    periods = forecast_data.get('properties', {}).get('periods', [])
    
    times = []
    temperatures = []
    cloud_covers = []

    for period in periods:
        times.append(pd.to_datetime(period['startTime']))
        temperatures.append(period['temperature'])
        cloud_cover = 100 if 'Cloudy' in period['shortForecast'] else 0
        cloud_covers.append(cloud_cover)
    
    weather_df = pd.DataFrame({
        'time': times,
        'temperature': temperatures,
        'cloud_cover': cloud_covers
    }).set_index('time')
    
    return weather_df

### 2️⃣ PVLib Solar Power Simulation ###
def simulate_solar(weather_df, latitude, longitude):
    # PV system parameters
    # Fetch standard module parameters from SAM
    sandia_modules = pvsystem.retrieve_sam('sandiamod')
    module_parameters = sandia_modules['Canadian_Solar_CS5P_220M___2009_']

    sandia_inverters = pvsystem.retrieve_sam('sandiainverter')
    inverter_parameters = sandia_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']

    system = pvsystem.PVSystem(
        module_parameters=module_parameters,
        inverter_parameters=inverter_parameters,
        temperature_model_parameters=temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
    )
    
    location_data = location.Location(latitude, longitude, tz='Etc/GMT+7', altitude=1200)
    
    mc = modelchain.ModelChain(system, location_data, dc_model='sapm', ac_model='sandia', aoi_model='no_loss', spectral_model='no_loss')

    # Solar Position and Clear-Sky Irradiance
    weather_df['dni'] = 800 * (1 - weather_df['cloud_cover'] / 100)  # Approximate DNI
    weather_df['ghi'] = 1000 * (1 - weather_df['cloud_cover'] / 100)  # Approximate GHI
    weather_df['dhi'] = weather_df['ghi'] - weather_df['dni']

    mc.run_model(weather=weather_df)

    return mc.results.ac

### 3️⃣ Combine Weather Data with PV Simulation ###
latitude = 31.77  # El Paso, TX
longitude = -106.48

weather_data = get_weather_data(latitude, longitude)
power_output = simulate_solar(weather_data, latitude, longitude)

# Plot Results
plt.figure(figsize=(12, 6))
plt.plot(weather_data.index, power_output, label='Solar Power Output (AC)')
plt.xlabel('Time')
plt.ylabel('Power (W)')
plt.title('Solar Power Simulation using NWS Forecast')
plt.grid(True)
plt.legend()
plt.show()
