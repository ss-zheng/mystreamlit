import requests
import json

def navcanada_request(icaos, options):
    # The base URL for the API request
    url = 'https://plan.navcanada.ca/weather/api/alpha/'

    # Parameters to be included in the request
    params = {
        'site': icaos,
        'alpha': options["alpha"]  # Specifying the options you want to pass
    }

    # Headers to be included in the request
    headers = {
        'authority': 'plan.navcanada.ca',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'referer': 'https://plan.navcanada.ca/wxrecall/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'x-requested-with': 'XMLHttpRequest'
    }

    # Making the GET request
    response = requests.get(url, params=params, headers=headers)

    # Checking if the request was successful
    filtered_data = []
    if response.status_code == 200:
        for item in json.loads(response.text)['data']:
            if any(icao_id in item['text'] for icao_id in icaos):
                filtered_data.append(item)
        # Process the response if needed
        return sorted(filtered_data, key=lambda x: x['startValidity'], reverse=True) # For example, print the response text
    else:
        raise f"Request failed with status code: {response.status_code}"
    
# print(navcanada_request(["CYXX"], options={"alpha": ['sigmet', 'airmet', 'notam', 'metar']}))
navcanada_request(["CYXX"], options={"alpha": ['notam']})