import os
import requests
from urllib.parse import quote_plus

from flask import Flask, render_template, request, session, redirect, url_for
from .core_requests import get_endorsements, get_roster, get_logins, get_station_data, get_rating, required_courses, get_theory_roster
from .monitor_login import check_connection
from dotenv import load_dotenv


load_dotenv()
oauth_auth = os.getenv('OAUTH_AUTH')
oauth_user = os.getenv('OAUTH_USER')
oauth_token = os.getenv('OAUTH_TOKEN')
oauth_scopes = os.getenv('OAUTH_SCOPES')

def login_url():
    id = os.environ['OAUTH_CLIENT_ID']
    redirect_url = quote_plus(f'{os.getenv("APP_URL")}/callback')
    url = f"{oauth_auth}?client_id={id}&response_type=code&redirect_uri={redirect_url}&scope={oauth_scopes}"
    return url


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = os.environ['FLASK_SECRET_KEY']
    @app.route('/', methods=('GET', 'POST'))
    def main():
        tr = get_theory_roster()

        user_id = session.get('user_id')
        if user_id is None:
            return redirect(login_url())
        cid = int(user_id)
        if request.method == 'POST':
            # Check whether ID exists
            try:
                rating = get_rating(cid)
            except:
                rating = False
                out = {
                    'may_control': False,
                    'website_msg': 'The controller ID seems to be incorrect.'
                }
                # may_control, msg = False, 'The controller ID seems to be incorrect.'
            if rating:
                solos = get_endorsements('solo')
                t1 = get_endorsements('tier-1')
                t2 = get_endorsements('tier-2')
                roster = get_roster()
                datahub = get_station_data()
                connection = {
                    'cid': cid,
                    'callsign': request.form['station'].upper(),
                    'name': '',
                    'rating': rating,
                    'facility': 5,
                    'frequency': 'website'
                }
                out = check_connection(connection, datahub, solos, t1, t2, roster)

            is_ctr_sector = request.form['station'].upper().split('_')[-1] == 'CTR'
            fam_msg = is_ctr_sector and out['may_control']

            return render_template('main.html', request=request, out=out, fam_msg=fam_msg, name=session.get('user_name'), tr=tr)
        else:
            return render_template('main.html', request=request, name=session.get('user_name'), tr=tr)

    @app.route('/callback')
    def callback():
        session.clear()
        code = request.args.get('code')
        auth_url = f"{oauth_token}"
        payload = {
            'grant_type': 'authorization_code',
            'client_id': os.environ['OAUTH_CLIENT_ID'],
            'client_secret': os.environ['OAUTH_CLIENT_SECRET'],
            'code': code,
            'redirect_uri': f'{os.getenv("APP_URL")}/callback'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        response = requests.request("POST", auth_url, headers=headers, data=payload)
        if response.status_code != 200:
            return redirect(url_for('main'))
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {response.json()["access_token"]}'
        }
        response = requests.request("GET", f"{oauth_user}", headers=headers)
        if response.status_code != 200:
            return redirect(url_for('main'))
        session['user_id'] = response.json()['data']['cid']
        session['user_name'] = response.json()['data']['personal']['name_first']
        return redirect(url_for('main'))

    @app.route('/logout')
    def logout():
        session.clear()
        return render_template('logout.html')

    return app
