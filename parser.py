from bs4 import BeautifulSoup

def parse_search(html):
    with open("search_results.html", "w") as text_file:
        text_file.write(html)
    soup = BeautifulSoup(html, 'html.parser')
    cases = []
    for row in soup.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) != 5:
            continue
        case = {
            'id': list(cols[0].stripped_strings)[0].replace(u'\xa0', u' '),
            'title': cols[1].string,
            'name': cols[2].string,
            'dob': cols[3].string,
            'role': cols[4].string
        }
        if case['id'] == 'Case ID':
            continue
        cases.append(case)
    return cases

def parse_case_summary(html, case):
    with open("cases/" + case['id'] + "_summary.html", "w") as text_file:
        text_file.write(html)
    soup = BeautifulSoup(html, 'html.parser')
    case['county'] = soup.find_all('tr')[2].find_all('td')[1].string

def parse_case_charges(html, case):
    with open("cases/" + case['id'] + "_charges.html", "w") as text_file:
        text_file.write(html)
    soup = BeautifulSoup(html, 'html.parser')
    charges = []
    cur_charge = None
    cur_section = None
    rows = soup.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        texts = [
            ''.join(col.find_all(text=True))
                .replace(u'\xa0', u' ')
                .replace('\r', '')
                .replace('\n', '')
                .replace('\t', '')
                .strip()
            for col in cols
        ]

        if len(texts) == 0:
            continue
        if texts[0].startswith("Count"):
            if cur_charge is not None:
                charges.append(cur_charge)
            cur_charge = {}

        if len(texts) == 2:
            if texts[1] == "Charge":
                cur_section = "Charge"
            if texts[1] == "Adjudication":
                cur_section = "Adjudication"
            if texts[1] == "Sentence":
                cur_section = "Sentence"
        
        if cur_section == "Charge":
            if len(texts) >= 5 and texts[3].startswith("Description:"):
                cur_charge['description'] = texts[4]
            if len(texts) >= 3 and texts[1].startswith("Offense Date:"):
                cur_charge['offenseDate'] = texts[2]
        
        if cur_section == "Adjudication":
            if len(texts) >= 5 and texts[1].startswith("Adj.:"):
                cur_charge['disposition'] = texts[2]
                cur_charge['dispositionDate'] = texts[4]

    if cur_charge is not None:
        charges.append(cur_charge)
    case['charges'] = charges

def parse_case_financials(html, case):
    with open("cases/" + case['id'] + "_financials.html", "w") as text_file:
        text_file.write(html)
    soup = BeautifulSoup(html, 'html.parser')
    financials = []
    rows = soup.find('form').find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if cols[1].string == 'Detail':
            continue
        financials.append({
            'detail': cols[1].string,
            'amount': cols[4].string,
            'paid': cols[5].string,
            'paidDate': cols[6].string
        })
    case['financials'] = financials
