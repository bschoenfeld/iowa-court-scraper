from flask import Flask, render_template, request
from reader import Reader
import ast
import os
import parser

app = Flask(__name__)

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
    #if request.form['password'] != os.environ['password']:
    #    return "ERROR"

    #reader = get_reader()
    #if reader is None:
    #    return "ERROR"

    first_name = request.form['firstname']
    last_name = request.form['lastname']

    print "Searching ", first_name, last_name
    #result = reader.search(first_name, last_name)
    #reader.logoff()

    result = None
    with open("search_results.html", "r") as text_file:
        result = text_file.read()

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
    data = request.form.getlist('caseIds')
    case_ids = [case_id for ids in data for case_id in ast.literal_eval(ids)]
    return "OK"

if __name__ == "__main__":
	app.run()