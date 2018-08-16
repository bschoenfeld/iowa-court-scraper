from bs4 import BeautifulSoup
from openpyxl import load_workbook
from os import listdir
from pprint import pprint
import parser

code_map = {
    "GUILTY": "GTR",
    "GUILTY BY COURT": "GTR",
    "GUILTY - NEGOTIATED/VOLUN PLEA": "GPL",
    "CONVERT TO SIMPLE MISDEM": "GPL",
    "ACQUITTED": "ACQ",
    "DISMISSED": "DISM",
    "DISMISSED BY COURT": "DISM",
    "DISMISSED BY OTHER": "DISM",
    "DEFERRED": "DEF",
    "NOT GUILTY": "ACQ",
    "WAIVED TO ADULT COURT": "JWV",
    "ADJUDICATED": "JUV",
    "WITHDRAWN": "WTHD",
    "NOT FILED": "NOTF"
}

def get_disposition_code(dispositions):
    if len(dispositions) == 0:
        return "NOTF"

    code = "OTH"
    date = None
    for x in dispositions:
        # NOTE - 01311  SRCR036699 has a withdrawn charge ealier than conviction
        if date is None:
            date = x[1]
        elif date != x[1]:
            continue

        disposition = x[0].replace("DNU-", "")
        if disposition and disposition not in code_map:
            print disposition
        if code == "GTR" or code == "GPL":
            continue
        if not disposition:
            code = "NOTF"
        elif disposition not in code_map:
            code = "OTH"
        else:
            code = code_map[disposition]
    return code

def get_finance_column(detail):
    if "FINE" in detail:
        return "J" # FINE
    if "FILING" in detail:
        return "K" # FILING
    if "INDIGENT DEFENSE" in detail:
        return "L" # INDIGENT DEFENSE
    if "SURCHARGE" in detail:
        return "M" # SURCHARGE
    if "RESTITUTION" in detail:
        return "O" # RESTITUTION
    if "THIRD PARTY" in detail:
        return "P" # THIRD PARTY
    if "SHERIFF" in detail:
        return "Q" # SHERIFF

    if "COLLECTION BY CO ATTY" in detail:
        return "S" # UNKNOWN
    if "DELINQUENT REVOLVING FUND" in detail:
        return "S" # UNKNOWN
    return None

wb = load_workbook('CRS 2.3.2.xlsx')
ws = wb['CASE DATA']

case_ids = []
files = listdir("./cases/")
for f in files:
    if f.endswith(".html") and f != "search_results.html":
        case_ids.append(f.split("_")[0])
case_ids = list(set(case_ids))
print len(case_ids)

unknowns = []
cur_row = 4
for case_id in case_ids:
    case = {'id': case_id}
    #print "Collecting " + case['id']

    with open("cases/" + case['id'] + "_summary.html", "r") as text_file:
        parser.parse_case_summary(text_file.read(), case)

    with open("cases/" + case['id'] + "_charges.html", "r") as text_file:
        parser.parse_case_charges(text_file.read(), case)

    with open("cases/" + case['id'] + "_financials.html", "r") as text_file:
        parser.parse_case_financials(text_file.read(), case)

    dispositions = [(c['disposition'], c['dispositionDate']) for c in case['charges']]
    #print case['id']
    #print dispositions
    #get_disposition_code(dispositions)

    for f in case['financials']:
        if not f['detail'].strip():
            continue
        col = get_finance_column(f['detail'])
        if col is None:
            unknowns.append(f['detail'])

    i = str(cur_row)
    ws['A' + i] = case['id']
    ws['B' + i] = case['county']
    cur_row += 1

pprint(set(unknowns))
wb.save("CRS 2.3.2_test.xlsx")
        