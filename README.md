# login-monitor

This app monitors the logins onto German stations to check whether the controllers have the required rating and endorsements and passed the required Moodle courses.
If a discrepancy is identified, it is communicated via Discord.
The app additionally provides canistaffit.vatger.de, which allows controllers to check whether they are allowed to staff a certain position.

## Contact

|         Name         | Responsible for |      Contact       |
| :------------------: | :-------------: | :----------------: |
| Felix S. - 1439797   |       *         | `atd[at]vatger.de` |

## Prerequisites
- **Python**

## Running the Website

1. Run `pip install -r requirements.txt`
2. Run `flask --app monitor run`

## API

`GET /api/check` allows other services to check whether a controller may staff a station.

**Query parameters:**

| Parameter      | Type   | Description                                  |
| -------------- | ------ | --------------------------------------------- |
| `token`        | string | Shared secret, must match `API_TOKEN`         |
| `user_id`      | int    | Controller CID                                |
| `rating`       | int    | Controller's VATSIM rating ID                 |
| `station_name` | string | Station callsign, e.g. `EDDF_TWR`             |

**Response:**

```json
{
  "may_control": true,
  "reason": "You may control EDDF_TWR.",
  "required_courses": [],
  "solo": {
    "expiry": "2026-08-08T21:14:30.224Z",
    "max_days": 30
  }
}
```

`solo` is `null` unless the controller's access to the station is based on a solo endorsement.
