from bs4 import BeautifulSoup
from opener import Opener
from reader import Reader
import os
import parser

first = "Allen"
last = "Adams"

reader = Reader(Opener())
reader.init()
reader.login(os.environ['username'], os.environ['password'])

try:
    print "Searching"
    result = reader.search(first, last)
    cases = parser.parse_search(result)

    for case in cases:
        print "Collecting " + case['id']
        result = reader.case_summary(case['id'])
        parser.parse_case_summary(result, case)

        result = reader.case_charges()
        parser.parse_case_charges(result, case)

        result = reader.case_financials()
        parser.parse_case_financials(result, case)
except:
    print "Search failed"

reader.logoff()
print "Logged Off"
