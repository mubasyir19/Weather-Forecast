from fastapi import FastAPI, HTTPException
import httpx
import xmltodict

app = FastAPI()

async def fetch_xml_data(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.text
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch XML data. Status code: {response.status_code}")

@app.get('/')
def root():
    return {"message": "Welcome to API CloudByMe"}

@app.get('/weather')
async def getWeather():
    xml_url = 'https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-Indonesia.xml'
    
    try:
        xml_data = await fetch_xml_data(xml_url)
        dataParse = xmltodict.parse(xml_data)       
        
        weather_data = [
                {
                    'Id': kota['@id'],
                    'Kota': kota['@description'],
                    'Provinsi': kota['@domain'],
                    'Latitude': kota['@latitude'],
                    'Longtitude': kota['@longitude'],
                    'Coordinate': kota['@coordinate'],
                    'Temperature': next((param for param in kota['parameter'] if param['@id'] == 't'), None),
                    'MaxTemperature': next((param for param in kota['parameter'] if param['@id'] == 'tmax'), None),
                    'MinTemperature': next((param for param in kota['parameter'] if param['@id'] == 'tmin'), None),
                    'Weather': next((param for param in kota['parameter'] if param['@id'] == 'weather'), None),
                    'Humidity': next((param for param in kota['parameter'] if param['@id'] == 'hu'), None),
                    'MaxHumidity': next((param for param in kota['parameter'] if param['@id'] == 'humax'), None),
                    'MinHumidity': next((param for param in kota['parameter'] if param['@id'] == 'humin'), None),
                    'WindDirection': next((param for param in kota['parameter'] if param['@id'] == 'wd'), None),
                    'WindSpeed': next((param for param in kota['parameter'] if param['@id'] == 'ws'), None),
                }
                for kota in dataParse['data']['forecast']['area']
            ]
        
        return {"data": weather_data}
    
    except httpx.HTTPError as http_err:
        raise HTTPException(status_code=http_err.response.status_code, detail=f"HTTP error: {http_err}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(err)}")