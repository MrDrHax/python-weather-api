from datetime import datetime
import fastapi
import httpx
import os
from pydantic import BaseModel

# Response models for the API
class WeatherData(BaseModel):
    '''Weather data model. Contains the maximum temperature, minimum temperature and date.'''

    temp_max: float
    temp_min: float
    date: str

class CityData(BaseModel):
    '''City data model. Contains the city id, slug, state, latitude, longitude and a list of weather data for the next 7 days.'''
    id : int
    slug : str
    state : str
    lat : float
    long : float
    weather : list[WeatherData]

# Prep
weather_api_key = os.getenv('WEATHER_API_KEY', "none")

if weather_api_key == "none":
    raise Exception("ERROR: No weather api key found. Please provide one in the WEATHER_API_KEY environment variable.")

app = fastapi.FastAPI()

headers = {
    "User-Agent": "WeatherAgent/1.0"
}

# Routes
@app.get("/weather/{city}", 
         responses={
             200: {"model": list[CityData]}, 
             400: {"description": "City name too short. Must be 3 characters or more (10)"}, 
             500: {"description": "Error fetching city data (1)"}
             },
         tags=["weather", "cities"])
async def weather(city: str) -> list[CityData]:
    '''Get the weather forecast for the next 7 days for a given city in Mexico.'''

    if len(city) < 3:
        raise fastapi.HTTPException(status_code=400, detail="City name too short. Must be 3 characters or more (10)")
    
    # Fetch city data and coordinates
    async with httpx.AsyncClient() as client:
        try:
            city_request = f"https://search.reservamos.mx/api/v2/places?q={city}"
            response = await client.get(city_request, headers=headers)
            response.raise_for_status() 
            city_data = response.json()
        except httpx.HTTPStatusError as e:
            raise fastapi.HTTPException(status_code=500, detail="Error fetching city data (1)")
        except httpx.RequestError as e:
            raise fastapi.HTTPException(status_code=500, detail="Error fetching city data (2)")

    toReturn = []

    # Fetch weather data for each city
    for c in city_data:
        # Filter only cities in Mexico
        if c['result_type'] == 'city' and c['country'] == 'México':
            data = CityData(id = c['id'], slug = c['slug'], state = c['state'], lat = c['lat'], long = c['long'], weather = [])
            
            # Fetch weather data
            async with httpx.AsyncClient() as client:
                try:
                    weather_request = f"https://api.openweathermap.org/data/2.5/onecall?lat={data.lat}&lon={data.long}&exclude=current,minutely,hourly&units=metric&appid={weather_api_key}"
                    response = await client.get(weather_request, headers=headers)
                    response.raise_for_status()
                    weather_data = response.json()
                except httpx.HTTPStatusError as e:
                    raise fastapi.HTTPException(status_code=500, detail="Error fetching weather data (3)")
                except httpx.RequestError as e:
                    raise fastapi.HTTPException(status_code=500, detail="Error fetching weather data (4)")

            # Parse weather data
            for w in weather_data['daily']:
                date_object = datetime.fromtimestamp(w['dt'])

                # Format the datetime object to a string in dd-mm-yyyy format
                formatted_date = date_object.strftime('%d-%m-%Y')

                data.weather.append(WeatherData(temp_max = float(w['temp']['max']), temp_min = float(w['temp']['min']), date = formatted_date))

            toReturn.append(data)

    return toReturn

