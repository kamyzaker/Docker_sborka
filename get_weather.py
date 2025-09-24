import requests



def get(q: str):
    url = 'https://api.openweathermap.org/data/2.5/weather'
    weather_items = {
    'q': q, #город
    'appid': 'bbb83a07f5323c28aab81812b9d816bc',
    'units': 'metric',
    'lang': 'ru',
}
    response = requests.get(url, params=weather_items)
    if response.status_code == 200:
        data = response.json()
        return data['weather'][0]['description']
    else:
        return(f"Ошибка: {response.status_code} = {response.text}")
    

