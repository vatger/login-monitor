import requests
from dotenv import load_dotenv
import os


load_dotenv()

api_key = os.getenv('CORE_API')


headers = {
        'Accept': 'application/json'
    }


def split_compare(cs1: str, cs2: str) -> [bool, str]:
    return cs1.split('_')[0] == cs2.split('_')[0] and cs1.split('_')[-1] == cs2.split('_')[-1]


def get_station_data() -> list[dict]:
    r = requests.get('https://raw.githubusercontent.com/VATGER-Nav/datahub/main/data.json', headers=headers)
    return r.json()


def get_endorsements(type: str) -> list[dict]:
    eud_header = {'X-API-KEY': api_key,
              'accept': 'application/json'}
    return requests.get(f'https://core.vateud.net/api/facility/endorsements/{type}', headers=eud_header).json()['data']


def get_logins() -> list[dict]:
    r = requests.get('https://df.vatsim-germany.org/datafeed/controllers', headers=headers).json()['data']
    connections = [x for x in r if (x['callsign'][:2] in ['ED', 'ET'] and x['callsign'][:4] != 'EDYY')]
    return connections


def get_roster() -> list[dict]:
    eud_header = {'X-API-KEY': api_key,
                  'accept': 'application/json'}
    return requests.get(f'https://core.vateud.net/api/facility/roster', headers=eud_header).json()['data']['controllers']


def get_rating(id: int) -> int:
    return requests.get(f'https://api.vatsim.net/api/ratings/{id}/').json()['rating']


def is_course_required(callsign: str) -> bool:
    courses = requests.get('https://raw.githubusercontent.com/VATGER-ATD/required-courses/main/courses.json').json()
    required = [course for course in courses if split_compare(callsign, course['station'])]
    return len(required) > 0
