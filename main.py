from datetime import datetime, timedelta
from data_manager import ApiCall
import requests
import os
from dotenv import load_dotenv
from twilio.rest import Client
from pprint import pprint

# call loadenv
load_dotenv()

# CONSTANTS
SHEETY_URL_ENDPOINT = os.getenv("SHEETY_URL_ENDPOINT")
TEQUILIA_LOCATION_ENDPOINT = "https://tequila-api.kiwi.com/locations/query"
TEQUILIA_SEARCH = "https://tequila-api.kiwi.com/v2/search"

SHEETY_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('SHEETY_AUTH')}"
}
TEQUILIA_HEADERS = {
    "apikey": os.getenv("TEQUILIA_API_KEY")
}

# get all the data from the google spreadsheet
google_sheet = requests.get(url=SHEETY_URL_ENDPOINT, headers=SHEETY_HEADERS)
sheet_data = google_sheet.json()
print(sheet_data)

# get the iata code from tequilia for each of the city on the spreadsheet
for row in sheet_data["prices"]:
    iata_search_parameters = {
        "term": row["city"],
        "locale": "en-US"
    }

    iata_tequilia = requests.get(url=TEQUILIA_LOCATION_ENDPOINT, params=iata_search_parameters,
                                 headers=TEQUILIA_HEADERS)
    iata_result = iata_tequilia.json()

    iata_code = iata_result['locations'][0]['code']

    # updating sheety back with the iata code for each location
    if row['iata'] == "":
        SHEETY_UPDATE_ENDPOINT = f"{os.getenv('SHEETY_UPDATE_ENDPOINT')}{row['id']}"
        sheety_update_parameters = {
            "price": {
                "iata": iata_code
            }
        }
        sheety_update = requests.put(url=SHEETY_UPDATE_ENDPOINT, json=sheety_update_parameters, headers=SHEETY_HEADERS)
        sheety_update_response = sheety_update.text
        print(sheety_update_response)

# getting flight information for each city on the google sheet using the tequlia search api.
for city in sheet_data["prices"]:
    iata_code = city['iata']
    tomorrow = datetime.now() + timedelta(days=1)
    six_month_from_today = datetime.now() + timedelta(days=(6 * 30))

    flight_search_parameters = {
        "fly_from": "ALB",
        "fly_to": iata_code,
        "date_from": tomorrow.strftime("%d/%m/%Y"),
        "date_to": six_month_from_today.strftime("%d/%m/%Y"),
        "flight_type": "round",
        "nights_in_dst_from": city["minimal"],
        "nights_in_dst_to": city["maximal"],
        "one_for_city": 1,
        "curr": "USD"
    }

    search_response = requests.get(url=TEQUILIA_SEARCH, params=flight_search_parameters, headers=TEQUILIA_HEADERS)
    flight = search_response.json()["data"]
    # extract info from data object
    price = flight[0]["price"]
    origin_city = flight[0]["cityFrom"]
    origin_airport = flight[0]["flyFrom"]
    destination_city = flight[0]["cityTo"]
    destination_airport = flight[0]["flyTo"]
    out_date = flight[0]["route"][0]["local_departure"].split("T")[0]
    return_date = flight[0]["route"][-1]["local_arrival"].split("T")[0]
    stop_overs = len(flight[0]["route"]) - 2
    if price < city['lowestPrice']:
        twilio_api_key = os.getenv("TWILIO_API_KEY")
        account_sid = os.getenv("ACCOUNT_SID")
        auth_token = os.getenv("AUTH_TOKEN")

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=f"Low price alert! Only ${price} to fly from Albany to {city['city']} from {out_date} to {return_date}"
                 f"with {stop_overs} stopovers",
            from_=os.getenv("FROM_NUMBER"),
            to=os.getenv("TO_NUMBER")
        )
        print(message.status)
