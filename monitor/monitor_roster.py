import datetime
import urllib.request
import json
from datetime import timedelta, datetime
from cachetools import cached, TTLCache

from .core_requests import get_roster, get_endorsements, make_request


from tqdm import tqdm


viable_suffixes = {
    # endorsement: [suffixes]
    "APP": ["APP", "DEP"],
    "TWR": ["APP", "DEP", "TWR"],
    "GNDDEL": ["APP", "DEP", "TWR", "GND", "DEL"],
}

ctr_topdown = {
    # APT: [Stations]
    "EDDB": ["EDWW_F_CTR", "EDWW_B_CTR", "EDWW_K_CTR", "EDWW_M_CTR", "EDWW_CTR"],
    "EDDH": ["EDWW_H_CTR", "EDWW_A_CTR", "EDWW_W_CTR", "EDWW_CTR"],
    "EDDF": [
        "EDGG_GIN_CTR",
        "EDGG_RUD_CTR",
        "EDGG_DKB_CTR",
        "EDGG_BAD_CTR",
        "EDGG_KTG_CTR",
    ],
    "EDDK": ["EDGG_PAH_CTR"],
    "EDDL": ["EDGG_PAH_CTR"],
    "EDDM": ["EDMM_NDG_CTR", "EDMM_ZUG_CTR", "EDMM_RDG_CTR"],
}


def suffix_condition(endorsement_apt: str, endorsement_station: str, callsign: str):
    cs_apt = callsign.split("_")[0]
    cs_station = callsign.split("_")[-1]
    return (
        cs_apt == endorsement_apt and cs_station in viable_suffixes[endorsement_station]
    )


@cached(cache=TTLCache(maxsize=float("inf"), ttl=60 * 60))
def get_connections(id: int, days_delta: int) -> list[dict]:
    dt = datetime.now() - timedelta(days=days_delta)
    with urllib.request.urlopen(
        f"https://api.vatsim.net/api/ratings/{id}/atcsessions/?start={dt.date()}"
    ) as url:
        connections = json.load(url)["results"]
    return connections


def calculate_activity(endorsement: str, connections: list[dict]) -> float:
    activity_min = 0
    if endorsement.split("_")[-1] == "CTR":
        for connection in connections:
            if connection["callsign"] == endorsement:
                activity_min += float(connection["minutes_on_callsign"])
                if activity_min > 180:
                    return True
    else:
        station = endorsement.split("_")[-1]
        apt = endorsement.split("_")[0]
        stations_to_consider = ctr_topdown[apt]
        for connection in connections:
            if connection["callsign"] in stations_to_consider or suffix_condition(
                apt, station, connection["callsign"]
            ):
                activity_min += float(connection["minutes_on_callsign"])
                if activity_min > 180:
                    return True
    return activity_min > 180


def check_connection_history(id: int) -> bool:
    connections = get_connections(id, 365)
    for connection in connections:
        # Connection happened in the last year, can stay on roster
        if (connection["callsign"][:2] in ["ED", "ET"]) and connection["callsign"][
            :4
        ] != "EDYY":
            return True
        else:
            # Check whether last rating change happened in last year
            with urllib.request.urlopen(
                f"https://api.vatsim.net/api/ratings/{id}/"
            ) as url:
                res = json.load(url)["lastratingchange"]
            if res is not None:
                res = datetime.strptime(res, "%Y-%m-%dT%H:%M:%S")
                if res > datetime.now() - timedelta(days=365):
                    return True
    return False


if __name__ == "__main__":
    roster = get_roster()
    t1 = get_endorsements("tier-1")

    t2 = get_endorsements("tier-2")
    for id in tqdm(roster):
        if not check_connection_history(id):
            print(f"Removing {id} from roster")
            # Send email
            # make_request("delete", f"facility/roster/{id}")

    # Get roster again, remove all endorsements for users not on roster
    roster = get_roster()
    for endorsement in t1:
        if endorsement["user_cid"] not in roster:
            print(f"Removing {endorsement['user_cid']} from endorsements")
            # make_request("delete", f"facility/endorsements/{endorsement['id']}")
        else:
            # Check whether activity > 3 hours / 6 months
            connections = get_connections(endorsement["user_cid"], 180)
            if not calculate_activity(endorsement["callsign"], connections):
                print(f"Removing {endorsement['user_cid']} from endorsements")
                # make_request("delete", f"facility/endorsements/{endorsement['id']}")
    for endorsement in t2:
        if endorsement["user_cid"] not in roster:
            print(f"Removing {endorsement['user_cid']} from endorsements")
            # make_request("delete", f"facility/endorsements/{endorsement['id']}")
