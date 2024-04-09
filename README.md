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
