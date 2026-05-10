import requests
from datetime import datetime, timedelta

base_url = 'http://127.0.0.1:5000'

for days_back in [0, 1]:
    date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    try:
        response = requests.get(f'{base_url}/dashboard/{date}')
        data = response.json()
        print(f'Date: {date}')
        print(f'Alerts: {data.get("alertas_hoy", 0)}')
        print(f'Consumption: {data.get("consumo_total", 0)}')
        print()
    except Exception as e:
        print(f'Error for {date}: {str(e)[:100]}')
