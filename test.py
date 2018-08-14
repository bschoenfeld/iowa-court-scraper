from bs4 import BeautifulSoup
from openpyxl import load_workbook
from os import listdir
from pprint import pprint
import parser

wb = load_workbook('CRS 2.3.2.xlsx')
ws = wb['CASE DATA']

case_ids = []
files = listdir(".")
for f in files:
    if f.endswith(".html"):
        case_ids.append(f.split("_")[0])
case_ids = list(set(case_ids))

cur_row = 4
for case_id in case_ids:
    case = {'id': case_id}
    #print "Collecting " + case['id']

    with open(case['id'] + "_summary.html", "r") as text_file:
        parser.parse_case_summary(text_file.read(), case)

    with open(case['id'] + "_charges.html", "r") as text_file:
        parser.parse_case_charges(text_file.read(), case)

    with open(case['id'] + "_financials.html", "r") as text_file:
        parser.parse_case_financials(text_file.read(), case)

    for charge in case['charges']:
        if charge['disposition'] == '':
            print case['id']
            print charge
        print charge['disposition']

    i = str(cur_row)
    ws['A' + i] = case['id']
    ws['B' + i] = case['county']
    cur_row += 1

wb.save("CRS 2.3.2_test.xlsx")
