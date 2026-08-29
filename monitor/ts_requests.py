import requests
from cachetools import cached, TTLCache
import os
from dotenv import load_dotenv
from collections import defaultdict


headers = {
    'Accept': 'application/json'
}

load_dotenv()

fam_key = os.getenv('FAM_KEY')


@cached(cache=TTLCache(maxsize=float('inf'), ttl=60 * 60))
def get_fams():
    url = "http://docker.vatsim-germany.org:8016/api/familiarisations"
    response = requests.get(url, headers={"Authorization": f"Bearer {fam_key}"})

    if response.status_code == 200:
        data = response.json()
        data = data.get("data", [])
        result = defaultdict(list)
        for item in data:
            result[item["vatsim_id"]].append(item["sector"])
        return result
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None
