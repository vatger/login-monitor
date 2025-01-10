import requests
from cachetools import cached, TTLCache
from dotenv import load_dotenv
import os

from .helpers import split_compare

load_dotenv()

api_key = os.getenv('CORE_API')
df_link = os.getenv('DF_LINK')

vatger_api_base = os.getenv('VATGER_API_BASE')
vatger_api_token = os.getenv('VATGER_API_TOKEN')

headers = {
    'Accept': 'application/json'
}

eud_header = {
    'X-API-KEY': api_key,
    'Accept': 'application/json',
    'User-Agent': 'VATGER'
}


@cached(cache=TTLCache(maxsize=float('inf'), ttl=60*60*12))
def get_station_data() -> list[dict]:
    r = requests.get("https://raw.githubusercontent.com/VATGER-Nav/datahub/production/api/stations.json", headers=headers)
    return r.json()


@cached(cache=TTLCache(maxsize=float('inf'), ttl=60*60))
def get_endorsements(type: str) -> list[dict]:
    return requests.get(f'https://core.vateud.net/api/facility/endorsements/{type}', headers=eud_header).json()['data']


@cached(cache=TTLCache(maxsize=float('inf'), ttl=60*60))
def get_logins() -> list[dict]:
    r = requests.get(df_link, headers=headers).json()['data']
    connections = [x for x in r if (x['callsign'][:2] in ['ED', 'ET'] and x['callsign'][:4] != 'EDYY')]
    return connections


@cached(cache=TTLCache(maxsize=float('inf'), ttl=60*60))
def get_roster() -> list[dict]:
    return requests.get(f'https://core.vateud.net/api/facility/roster', headers=eud_header).json()['data'][
        'controllers']


@cached(cache=TTLCache(maxsize=1024, ttl=60*60))
def get_rating(id: int) -> int:
    return requests.get(f'https://api.vatsim.net/api/ratings/{id}/').json()['rating']


def check_course_completion(course: dict, cid: int) -> bool:
    course_id = course['link'].split('id=')[-1]
    header = {"Authorization": f"Token {vatger_api_token}"}
    r = requests.get(
        f"{vatger_api_base}moodle/course/{course_id}/user/{cid}/completion",
        headers=header,
    ).json()
    try:
        return r["completed"]
    except:
        return False


@cached(cache=TTLCache(maxsize=float('inf'), ttl=60*60))
def required_courses(callsign: str, cid: int) -> list[dict]:
    """

    :param callsign: Callsign of station
    :param cid: Controller ID
    :return: Dict of required courses that have not been passed
    """
    courses = requests.get('https://raw.githubusercontent.com/VATGER-ATD/required-courses/main/courses.json').json()
    res = [course for course in courses if split_compare(callsign, course['station'])]
    if res:
        courses = res[0]['courses']
        return [course for course in courses if not check_course_completion(course, cid)]
    else:
        return []
