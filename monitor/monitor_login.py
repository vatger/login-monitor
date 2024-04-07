from .core_requests import get_station_data, get_endorsements, get_logins, get_roster, split_compare
from .discord import send_message


ratings = {
    1: 'OBS',
    2: 'S1',
    3: 'S2',
    4: 'S3',
    5: 'C1'
}


required_rating = {
    'DEL': 2,
    'GND': 2,
    'TWR': 3,
    'APP': 4,
    'CTR': 5
}


def safe_get(data: dict, key: str) -> object:
    if key in data.keys():
        return data[key]
    else:
        return False


def check_connection(connection: dict, station_data: list[dict], solos: list[dict], t1: list[dict], t2: list[dict], roster: list[dict]) -> [bool, str]:
    if connection['facility'] == 0:
        return True, 'OBS', 'OBS'
    if connection['frequency'] == '199.998':
        return True, 'No primary', 'No primary'
    # Filter out EDW_APP
    if connection['callsign'] == 'EDW_APP':
        return True, 'EDW_APP', 'EDW_APP'
    user_has_solo = False
    user_has_t1 = False
    station_is_t1 = False
    # Try to get datahub entry from callsign
    if connection['cid'] not in roster:
        return False, f'{connection["cid"], connection["name"]} controlling {connection["callsign"]} not on roster.', 'You may not control this station as you are not on the roster.'

    if connection['frequency'] == 'website':
        data = [station for station in station_data if station['logon'] == connection['callsign']]
    else:
        data = [station for station in station_data if station['logon'][:4] == connection['callsign'][:4] and station['frequency'] == connection['frequency']]
    if data:
        data = data[0]
    else:
        return False, f'No station found {connection["callsign"], connection["cid"], connection["name"]}', 'Station not found'

    # Rating check
    station_type = connection['callsign'].split('_')[-1]
    if station_type == 'DEP':
        station_type = 'APP'
    if required_rating[station_type] > connection['rating']:
        # Check for solo endorsement
        user_solos = [solo for solo in solos if solo['user_cid'] == connection['cid']]
        if user_solos:
            solo_apt, solo_station = user_solos[0]['position'].split('_')[0], user_solos[0]['position'].split('_')[-1]
            user_apt, user_station = connection['callsign'].split('_')[0], station_type
            # Match solo endorsement and user
            if solo_apt == user_apt and solo_station == user_station:
                user_has_solo = True
        elif station_type == 'TWR':
            # Is TWR part of T1 Program?
            if not safe_get(data, 's1_twr') and connection['rating'] == 2:
                return False, f'{connection["cid"], connection["name"]} controlling TWR {connection["callsign"]} not in S1 TWR Program.', 'This TWR may not be controlled with S1.'
        else:
            return False, f'{connection["cid"], connection["name"]} controlling station {connection["callsign"]} without rating or solo.', 'You need a higher rating to control this position.'
    # Restricted station check
    if safe_get(data, 'gcap_status') == 'AFIS':
        user_endorsement = [endorsement for endorsement in t2 if endorsement['user_cid'] == connection['cid'] and endorsement['position'] == 'EDXX_AFIS']
        if not user_endorsement:
            return False, f'{connection["cid"], connection["name"]} has no AFIS endorsement for {connection["callsign"]}.', 'You need an AFIS endorsement to control this position.'
    elif safe_get(data, 'gcap_status') == '1':
        station_is_t1 = True
        user_endorsements = [endorsement for endorsement in t1 if endorsement['user_cid'] == connection['cid']]
        user_has_t1 = False
        for endorsement in user_endorsements:
            if station_type in ['DEL', 'GND']:
                solo_apt, solo_station = endorsement['position'].split('_')[0], endorsement['position'].split('_')[-1]
                user_apt, user_station = connection['callsign'].split('_')[0], station_type
                if solo_station == 'GNDDEL' and solo_apt == user_apt:
                    user_has_t1 = True
                    break
            else:
                if endorsement['position'] == connection['callsign']:
                    user_has_t1 = True
                    break
    if station_is_t1:
        if user_has_t1 or user_has_solo:
            return True, '', f'You may control {connection["callsign"]}.'
        else:
            return False, f'{connection["cid"], connection["name"]} has neither solo nor tier 1 endorsement for {connection["callsign"]}.', 'You need an endorsement for this station.'
    else:
        return True, '', f'You may control {data["logon"]}.'


if __name__ == '__main__':
    solos = get_endorsements('solo')
    t1 = get_endorsements('tier-1')
    t2 = get_endorsements('tier-2')
    roster = get_roster()
    logins = get_logins()
    datahub = get_station_data()
    for login in logins:
        check, msg, _ = check_connection(login, datahub, solos, t1, t2, roster)
        if not check:
            with open('/data/monitor/messaged.txt', 'r') as f:
                content = f.read()
            if not str(login['cid']) in content:
                send_message(msg)
                with open('/data/monitor/messaged.txt', 'a') as f:
                    f.write(str(login['cid']) + '\n')
