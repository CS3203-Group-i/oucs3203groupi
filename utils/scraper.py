import requests
from bs4 import BeautifulSoup

def fetch_classnav_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Example parsing logic
        data = soup.find_all('div', class_='class-info')
        return [item.text for item in data]
    else:
        raise Exception("Failed to fetch data from ClassNav")
