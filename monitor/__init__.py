from flask import Flask, render_template, request
from .core_requests import get_endorsements, get_roster, get_logins, get_station_data, get_rating, required_courses
from .monitor_login import check_connection


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    @app.route('/', methods=('GET', 'POST'))
    def main():
        if request.method == 'POST':
            # Check whether ID exists
            try:
                rating = get_rating(int(request.form['cid']))
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
                    'cid': int(request.form['cid']),
                    'callsign': request.form['station'].upper(),
                    'name': '',
                    'rating': rating,
                    'facility': 5,
                    'frequency': 'website'
                }
                out = check_connection(connection, datahub, solos, t1, t2, roster)

            is_ctr_sector = request.form['station'].upper().split('_')[-1] == 'CTR'
            fam_msg = is_ctr_sector and out['may_control']

            return render_template('main.html', request=request, out=out, fam_msg=fam_msg)
        else:
            return render_template('main.html', request=request)

    return app
