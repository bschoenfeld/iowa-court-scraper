from flask import Flask, render_template, request, send_file, session
from opener import Opener
from openpyxl import load_workbook
from pprint import pprint
from reader import Reader
import ast
import crs
import os
import parser

app = Flask(__name__)
app.secret_key = "NOTASECRET"

def get_reader():
    reader = Reader(Opener())
    reader.init()
    result = reader.login(os.environ['username'], os.environ['password'])
    if "The userID or password could not be validated" in result:
        return None
    return reader

@app.route('/')
def index():
	return render_template('start.html')

@app.route('/search', methods=['POST'])
def search():
    if request.form['password'] != os.environ['password']:
        return "ERROR"

    reader = get_reader()
    if reader is None:
        return "ERROR"

    session['firstname'] = request.form['firstname']
    session['lastname'] = request.form['lastname']

    print "Searching ", session['firstname'], session['lastname']
    result = reader.search(session['firstname'], session['lastname'])
    reader.logoff()

    #result = None
    #with open("search_results.html", "r") as text_file:
    #    result = text_file.read()

    print "Parsing results"
    cases = parser.parse_search(result)

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
    return render_template('search.html', cases=case_dict, keys=keys)

@app.route('/crs', methods=['POST'])
def get_crs():
    if 'firstname' not in session:
        return "ERROR"

    reader = get_reader()
    if reader is None:
        return "ERROR"

    print "Searching ", session['firstname'], session['lastname']
    result = reader.search(session['firstname'], session['lastname'])

    data = request.form.getlist('caseIds')
    case_ids = [case_id for ids in data for case_id in ast.literal_eval(ids)]
    
    wb = load_workbook('CRS 2.3.2.xlsx')
    ws = wb['CASE DATA']
    row = 4

    for case_id in case_ids:
        case = {'id': case_id}
        print "Collecting " + case['id']
        result = reader.case_summary(case['id'])
        parser.parse_case_summary(result, case)

        result = reader.case_charges()
        parser.parse_case_charges(result, case)

        result = reader.case_financials()
        parser.parse_case_financials(result, case)

        #with open("cases/" + case['id'] + "_summary.html", "r") as text_file:
        #    parser.parse_case_summary(text_file.read(), case)

        #with open("cases/" + case['id'] + "_charges.html", "r") as text_file:
        #    parser.parse_case_charges(text_file.read(), case)

        #with open("cases/" + case['id'] + "_financials.html", "r") as text_file:
        #    parser.parse_case_financials(text_file.read(), case)
        
        crs.process_case(case, ws, row)
        row += 1

    reader.logoff()
    
    wb.save("/tmp/CRS 2.3.2_test.xlsx")
    return send_file("/tmp/CRS 2.3.2_test.xlsx")

if __name__ == "__main__":
	app.run()