# README

This is a rails project that exposes an endpoint for the weather in a given place searches for existing locations in the city, and returns the list of expected weather.

The developed python version is:
- Python 3.10

(Python 3.10 + will probably work, anything before won't work)

# Configuration

Install dependencies with `pip install -r requeriments.txt`

# Running 

Run: `WEATHER_API_KEY="<key>" uvicorn main:app` 

To start the server.

To test an endpoint, make a GET request to `http://127.0.0.1:3000/weather/<city>`

```sh
curl -X 'GET' \
  'http://localhost:8000/weather/cdmx' \
  -H 'accept: application/json'
```

Docs available at http://localhost:8000/docs#/