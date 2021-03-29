from flask import Flask, jsonify, render_template, request, send_file, session, url_for, redirect
from openpyxl import load_workbook
from reader import Reader
import crs
import json
import os
import case_parser
import logging
from logging.config import dictConfig
import path_helper

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'flask': {
            'class': 'logging.FileHandler',
            'filename': path_helper.get_log('flask'),
            'mode': 'w',
            # 'maxBytes': 1024,
            # 'backupCount': 1
        },
        'http': {
            'class': 'logging.FileHandler',
            'filename': path_helper.get_log('http'),
            'mode': 'w',
            # 'maxBytes': 1024,
            # 'backupCount': 1
        },
        'stdout': {
            'class': 'logging.StreamHandler',
            'stream': 'stdout'
        },
    },
    'loggers': {
        'root': {
            'level': 'INFO',
            'formatters': 'default',
            'handlers': ['flask'],
            'propagate': False
        },
        'http': {
            'level': 'INFO',
            'formatters': 'default',
            'handlers': ['http'],
            'propagate': False
        },
        'app': {
            'level': 'INFO',
            'formatters': 'default',
            'handlers': ['stdout']
        }
    }
})

app = Flask(__name__)
app.secret_key = "pair6RAUD.flid.rhip"
tmp_dir = path_helper.get_tmp()

def get_reader(username=None, password=None, use_cookie_file=False):
    reader = Reader()
    # if cookies in session, we already logged in
    if 'cookies' in session:
        logging.info("cookies found in session. authorizing")
        reader.set_cookies(session['cookies'])
        # if session active (adv page returns non-empty), use it
        # otherwise relogin
        if reader.check_session():
            return reader, ""

    if username is None:
        print("Cannot login, no username provided")
        return (None, "No username provided")
    else:
        print("Logging in as ", username)
        reader.init()
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)

        # with open(tmp_dir + "cookies.txt", "wb") as text_file:
        #     text_file.write(reader.opener.get_cookies())

        result = reader.login(username, password)
        if "The userID or password could not be validated" in result:
            print("Bad User ID or password")
            return (None, "Bad User ID or password")

        if "Concurrent Login Error" in result:
            print("User already logged in")
            return (None, "User already logged in")

        print("Logged in")
    return reader, ""


def sleep_reader(reader):
    cookies = reader.get_cookies()
    if len(cookies):
        logging.info(f'Saving cookies {cookies}')
    session['cookies'] = cookies

def close_reader(reader):
    logging.info("Logging off")
    reader.logoff()
    session.pop('cookies', None)


@app.route('/')
def index():
    return render_template('start.html')

@app.route('/logout')
def logout():
    reader, error = get_reader(None, None, True)
    if reader is not None:
        reader.logoff()
    session.pop('cookies', None)
    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
    username = request.form['username']
    password = request.form['password']

    if not username.startswith("ILA"):
        return "Invalid Username"

    reader, error = get_reader(username, password)
    if reader is None:
        return error

    firstname = request.form['firstname']
    middlename = request.form['middlename']
    lastname = request.form['lastname']

    logging.info(f'Searching {firstname}, {middlename}, {lastname}', )
    result = reader.search(firstname, middlename, lastname)
    sleep_reader(reader)

    #result = None
    #with open("search_results.html", "r") as text_file:
    #    result = text_file.read()

    logging.info(f'Search Result: {len(result)} b. Parsing...')
    cases, too_many_results = case_parser.parse_search(result)

    case_dict = {}
    for case in cases:
        key = 'DOB-UNKNOWN ' + case['name']
        if case['dob']:
            key = "{}-{}-{} {}".format(
                case['dob'].split('/')[2],
                case['dob'].split('/')[0],
                case['dob'].split('/')[1],
                case['name']
            )
        if key not in case_dict:
            case_dict[key] = []
        case_dict[key].append(case['id'])
    keys = sorted([key for key in case_dict])
    return render_template('search.html', cases=case_dict, keys=keys, too_many_results=too_many_results)

@app.route('/case', methods=['POST'])
def get_case_details():
    if 'cookies' not in session:
        return "Bad session"

    reader, error = get_reader()
    if reader is None:
        return error

    case = {'id': request.form['caseId']}
    print(case)

    result = reader.case_summary(case['id'])
    case_parser.parse_case_summary(result, case)

    result = reader.case_charges()
    case_parser.parse_case_charges(result, case)

    result = reader.case_financials()
    case_parser.parse_case_financials(result, case)

    #with open("cases/" + case['id'] + "_summary.html", "r") as text_file:
    #    case_parser.parse_case_summary(text_file.read(), case)

    #with open("cases/" + case['id'] + "_charges.html", "r") as text_file:
    #    case_parser.parse_case_charges(text_file.read(), case)

    #with open("cases/" + case['id'] + "_financials.html", "r") as text_file:
    #    case_parser.parse_case_financials(text_file.read(), case)
    
    return jsonify(case)

@app.route('/crs', methods=['GET', 'POST'])
def generate_crs():
    if request.method == 'GET':
        if 'file' not in session:
            return "Bad session - no file"
        path = session['file']
        session.pop('file', None)
        return send_file(path)

    if 'cookies' not in session:
        return "Bad session"

    reader, error = get_reader()
    if reader is None:
        return error
    close_reader(reader)
    session.pop('cookies', None)

    data = json.loads(request.data)

    wb = load_workbook(f'{path_helper.get_dir()}/CRS 2.3.3.xlsx')
    ws = wb['CASE DATA']
    row = 4

    for case in data['cases']:
        print("Adding " + case['id'])
        crs.process_case(case, ws, row)
        row += 1

    fp = tmp_dir + "CRS 2.3.3.xlsx"
    wb.save(fp)
    session['file'] = fp
    return jsonify({'result': "success"})

@app.template_filter('pluralize')
def pluralize(number, singular = '', plural = 's'):
    if number == 1:
        return singular
    else:
        return plural

if __name__ == "__main__":
    app.run()