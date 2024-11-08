import requests
from dotenv import load_dotenv
import os


load_dotenv()
api_key = os.getenv("VATGER_API_KEY")


roster_warning = """
    Hi,
    we noticed that you have not been active in VATSIM Germany's airspace for a while.
    If you want to stay on our roster to continue controlling, please make sure connect at least once in the next 30 days.
    """

roster_msg = """
    Hi,
    due to inactivity, we have removed you from VATSIM Germany's roster.
    This means that you are no longer allowed to control in VATSIM Germany's airspace.
    To regain your controller privileges, kindly view the following information linked below.

    Please contact the ATD (atd@vatger.de) if you believe this was a mistake.
    """

endorsement_msg = (
    lambda positions: f"""
    Hi,
    due to inactivity, we have removed the following endorsements due to inactivity:
    {', '.join(positions)}.
    To regain your controller privileges, please request training in our forums.

    Please contact the ATD (atd@vatger.de) if you believe this was a mistake.
    """
)


endorsement_soon = (
    lambda positions: f"""
    Hi,
    you currently do not meet the activity requirements for the following endorsements:
    {', '.join(positions)}.
    Please ensure you meet the requirements (3 hours in 180 days) within the next 30 days to avoid removal.
    Please contact the ATD (atd@vatger.de) if you believe this is a mistake.
    """
)


def send_roster_msg(id: int):
    data = {
        "title": "Removal from VATGER Roster",
        "message": roster_msg,
        "source_name": "VATGER ATD",
        "link_text": "Returning to roster",
        "link_url": "https://knowledgebase.vatsim-germany.org/books/atc/page/returning-controllers",
    }
    header = {"Authorization": f"Token {api_key}"}
    r = requests.post(
        f"https://vatsim-germany.org/api/user/{id}/send_notification",
        data=data,
        headers=header,
    )
    return r.json()


def send_endorsement_msg(id: int, endorsements_lost: list[str]):
    data = {
        "title": "Endorsement Removal",
        "message": endorsement_msg(endorsements_lost),
        "source_name": "VATGER ATD",
    }
    header = {"Authorization": f"Token {api_key}"}
    r = requests.post(
        f"https://vatsim-germany.org/api/user/{id}/send_notification",
        data=data,
        headers=header,
    )
    return r.json()


def send_endorsement_warning(id: int, endorsements_lost: list[str]):
    data = {
        "title": "Endorsement Removal",
        "message": endorsement_soon(endorsements_lost),
        "source_name": "VATGER ATD",
    }
    header = {"Authorization": f"Token {api_key}"}
    r = requests.post(
        f"https://vatsim-germany.org/api/user/{id}/send_notification",
        data=data,
        headers=header,
    )
    return r.json()


def send_roster_warning(id: int):
    data = {
        "title": "Inactivity Warning",
        "message": roster_warning,
        "source_name": "VATGER ATD",
    }
    header = {"Authorization": f"Token {api_key}"}
    r = requests.post(
        f"https://vatsim-germany.org/api/user/{id}/send_notification",
        data=data,
        headers=header,
    )
    return r.json()
