import requests
from dotenv import load_dotenv
import os

from .helpers import split_compare


load_dotenv()

api_key = os.getenv('CORE_API')
df_link = os.getenv('DF_LINK')


headers = {
        'Accept': 'application/json'
    }


eud_header = {'X-API-KEY': api_key,
                   'accept': 'application/json',
                  'User-Agent': 'VATGER'}


def get_station_data() -> list[dict]:
    r = requests.get('https://raw.githubusercontent.com/VATGER-Nav/datahub/main/data.json', headers=headers)
    return r.json()


def get_endorsements(type: str) -> list[dict]:
    return requests.get(f'https://core.vateud.net/api/facility/endorsements/{type}', headers=eud_header).json()['data']


def get_logins() -> list[dict]:
    r = requests.get(df_link, headers=headers).json()['data']
    connections = [x for x in r if (x['callsign'][:2] in ['ED', 'ET'] and x['callsign'][:4] != 'EDYY')]
    return connections


def get_roster() -> list[dict]:
    return requests.get(f'https://core.vateud.net/api/facility/roster', headers=eud_header).json()['data']['controllers']


def get_rating(id: int) -> int:
    return requests.get(f'https://api.vatsim.net/api/ratings/{id}/').json()['rating']


def required_courses(callsign: str) -> list[dict]:
    courses = requests.get('https://raw.githubusercontent.com/VATGER-ATD/required-courses/main/courses.json').json()
    return [course for course in courses if split_compare(callsign, course['station'])]
