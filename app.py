from flask import Flask, jsonify, render_template, request, send_file, session
from opener import Opener
from openpyxl import load_workbook
from pprint import pprint
from reader import Reader
import ast
import crs
import json
import os
import case_parser

app = Flask(__name__)
app.secret_key = "NOTASECRET"

def get_reader(username=None, password=None, use_cookie_file=False):
    reader = Reader(Opener())
    if 'cookies' in session:
        print("Loading cookies")
        reader.opener.load_cookies(session['cookies'])
    elif use_cookie_file:
        print("Loading cookies from file")
        with open("/tmp/cookies.txt", "r") as text_file:
            cookies = text_file.read()
            print(cookies)
            reader.opener.load_cookies(cookies)
    elif username is None:
        print("Cannot login, no username provided")
        return (None, "No username provided")
    else:
        print("Logging in as ", username)
        reader.init()

        with open("/tmp/cookies.txt", "w") as text_file:
            text_file.write(reader.opener.get_cookies())
        
        result = reader.login(username, password)

        if "The userID or password could not be validated" in result:
            print("Bad User ID or password")
            return (None, "Bad User ID or password")

        if "Concurrent Login Error" in result:
            print("User already logged in")
            return (None, "User already logged in")

        print("Logged in")
    return (reader, "")

def sleep_reader(reader):
    print("Saving cookies")
    session['cookies'] = reader.opener.get_cookies()

def close_reader(reader):
    print("Logging off")
    reader.logoff()
    session.pop('cookies', None)

@app.route('/')
def index():
	return render_template('start.html')

@app.route('/logout')
def logout():
    reader, error = get_reader(None, None, True)
    if reader is None:
        return jsonify({'result': "Session not found"})
    close_reader(reader)
    return jsonify({'result': "Done"})

@app.route('/test')
def test():
    print("Parsing results")
    cases = case_parser.parse_search(None)
    return jsonify({'result': "Done"})

@app.route('/search', methods=['POST'])
def search():
    username = request.form['username']
    password = request.form['password']

    reader, error = get_reader(username, password)
    if reader is None:
        return error

    firstname = request.form['firstname']
    middlename = request.form['middlename']
    lastname = request.form['lastname']

    print("Searching ", firstname, middlename, lastname)
    result = reader.search(firstname, middlename, lastname)
    sleep_reader(reader)

    #result = None
    #with open("search_results.html", "r") as text_file:
    #    result = text_file.read()

    print("Parsing results")
    cases, too_many_results = case_parser.parse_search(result)

    case_dict = {}
    for case in cases:
        if not case['dob']: continue
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

    wb = load_workbook('CRS 2.3.3.xlsx')
    ws = wb['CASE DATA']
    row = 4

    for case in data['cases']:
        print("Adding " + case['id'])
        crs.process_case(case, ws, row)
        row += 1

    fp = "/tmp/CRS 2.3.3.xlsx"
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
