import datetime
import urllib.request
import json
from datetime import timedelta, datetime
from cachetools import cached, TTLCache

from .core_requests import get_roster, get_endorsements, make_request
from .msg import send_endorsement_msg, send_roster_msg, send_roster_warning
from .msg_atd import send_mail

from tqdm import tqdm
from time import sleep
import pandas as pd


viable_suffixes = {
    # endorsement: [suffixes]
    "APP": ["APP", "DEP"],
    "TWR": ["APP", "DEP", "TWR"],
    "GNDDEL": ["APP", "DEP", "TWR", "GND", "DEL"],
}

ctr_topdown = {
    # APT: [Stations]
    "EDDB": ["EDWW_F", "EDWW_B", "EDWW_K", "EDWW_M", "EDWW_C"],
    "EDDH": ["EDWW_H", "EDWW_A", "EDWW_W", "EDWW_C"],
    "EDDF": [
        "EDGG_G",
        "EDGG_R",
        "EDGG_D",
        "EDGG_B",
        "EDGG_K",
    ],
    "EDDK": ["EDGG_P"],
    "EDDL": ["EDGG_P"],
    "EDDM": ["EDMM_N", "EDMM_Z", "EDMM_R"],
}


def append_row(dataframe: pd.DataFrame, id: int, position: str, activity: float):
    row = [
        id,
        position,
        activity,
        f"https://stats.vatsim.net/stats/{id}?range=6months",
        f"https://core.vateud.net/manage/controller/{id}/view",
    ]
    new = pd.DataFrame(row, columns=dataframe.columns)
    if dataframe.empty:
        return new
    else:
        return pd.concat([dataframe, new], ignore_index=True)


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


def calculate_activity(endorsement: dict, connections: list[dict]) -> float:
    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    created_at = datetime.strptime(endorsement["created_at"], date_format)
    if datetime.now() - created_at < timedelta(days=180):
        return True
    activity_min = 0
    if endorsement["position"].split("_")[-1] == "CTR":
        for connection in connections:
            if connection["callsign"][:6] == endorsement["position"][:6]:
                activity_min += float(connection["minutes_on_callsign"])
                if activity_min > 180:
                    return activity_min
    else:
        station = endorsement["position"].split("_")[-1]
        apt = endorsement["position"].split("_")[0]
        stations_to_consider = ctr_topdown[apt]
        for connection in connections:
            if connection["callsign"][:6] in stations_to_consider or suffix_condition(
                apt, station, connection["callsign"]
            ):
                activity_min += float(connection["minutes_on_callsign"])
                if activity_min > 180:
                    return activity_min
    return activity_min


def check_connection_history(id: int, days: int) -> bool:
    connections = get_connections(id, days)
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
            else:
                return True
    return False


if __name__ == "__main__":
    removed_endorsements = {}
    columns = ["user_cid", "position", "activity", "connections", "Core"]
    endorsement_warnings = pd.DataFrame(columns=columns)
    warning_cids = []
    warning_positions = []
    warning_activities = []
    warning_connection_link = []
    warning_core_link = []
    roster = get_roster()
    t1 = get_endorsements("tier-1")
    t2 = get_endorsements("tier-2")
    # for id in tqdm(roster):
    #     sleep(2)
    #     if not check_connection_history(id, 365):
    #         # Send notification
    #         send_roster_msg(id)
    #         r = make_request("delete", f"facility/roster/{id}")
    #         print(id, r)
    #     elif not check_connection_history(id, 11 * 30):
    #         send_roster_warning(id)

    # Get roster again, remove all endorsements for users not on roster
    roster = get_roster()
    for endorsement in tqdm(t1[:15]):
        if endorsement["user_cid"] not in roster:
            print(
                make_request(
                    "delete", f"facility/endorsements/tier-1/{endorsement['id']}"
                )
            )
        else:
            # Check whether activity > 3 hours / 6 months
            sleep(2)
            connections180 = get_connections(endorsement["user_cid"], 180)
            sleep(2)
            connections150 = get_connections(endorsement["user_cid"], 150)
            if calculate_activity(endorsement, connections180) < 180:
                print(
                    f"Removing {endorsement['user_cid']} {endorsement['position']} from endorsements"
                )
                if endorsement["user_cid"] not in removed_endorsements.keys():
                    removed_endorsements[endorsement["user_cid"]] = [
                        endorsement["position"]
                    ]
                else:
                    removed_endorsements[endorsement["user_cid"]].append(
                        endorsement["position"]
                    )
                # make_request("delete", f"facility/endorsements/{endorsement['id']}")
            if calculate_activity(endorsement, connections150) < 180:  # elif!!
                print("Warning")
                warning_cids.append(endorsement["user_cid"])
                warning_positions.append(endorsement["position"])
                warning_activities.append(
                    round(calculate_activity(endorsement, connections150), 1)
                )
                warning_connection_link.append(
                    f"<a href='https://stats.vatsim.net/stats/{endorsement['user_cid']}?range=6months'>Stats</a>"
                )
                warning_core_link.append(
                    f"<a href='https://core.vateud.net/manage/controller/{endorsement['user_cid']}/view'>Core</a>"
                )
    endorsement_warnings["user_cid"] = warning_cids
    endorsement_warnings["position"] = warning_positions
    endorsement_warnings["activity"] = warning_activities
    endorsement_warnings["connections"] = warning_connection_link
    endorsement_warnings["Core"] = warning_core_link
    # for endorsement in t2:
    #     if endorsement["user_cid"] not in roster:
    #         print(f"Removing {endorsement['user_cid']} from endorsements")
    #         print(
    #             make_request(
    #                 "delete", f"facility/endorsements/tier-2/{endorsement['id']}"
    #             )
    #         )

    send_mail(endorsement_warnings.sort_values("user_cid"))
    # for id, endorsements_lost in removed_endorsements.items():
    #     print(send_endorsement_msg(id, endorsements_lost))
    #     print(id)
    #     sleep(2)
