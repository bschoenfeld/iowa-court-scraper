from decimal import Decimal

charge_code_map = {
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

def get_primary_charge(charges):
    if len(charges) == 0:
        return None

    charge = charges[0]
    charge['code'] = "OTH"
    date = None
    for c in charges:
        # NOTE - 01311  SRCR036699 has a withdrawn charge ealier than conviction
        if date is None:
            date = c['dispositionDate']
        elif date != c['dispositionDate']:
            continue

        disposition = c['disposition'].replace("DNU-", "")
        #if disposition and disposition not in charge_code_map:
        #    print disposition
        if charge['code'] == "GTR" or charge['code'] == "GPL":
            continue
        charge = c
        if not disposition:
            charge['code'] = "NOTF"
        elif disposition not in charge_code_map:
            charge['code'] = "OTH"
        else:
            charge['code'] = charge_code_map[disposition]
    return charge

def get_finance_column(detail):
    if "COLLECTION BY CO ATTY" in detail:
        return "S" # UNKNOWN
    if "DELINQUENT REVOLVING FUND" in detail:
        return "S" # UNKNOWN
        
    if "FINE" in detail:
        return "J" # FINE
    if "DEFERRED JUDGMENT CIVIL PENALTY" in detail:
        return "J" # FINE
    if "INFRACTIONS-PENALTIES AND FORFEITURES-CITY" in detail:
        return "J" # FINE
    if "NONSCHEDULED CHAPTER 321" in detail:
        return "J" # FINE
    if "SCHEDULED VIOLATION/NON-SCHEDULED" in detail:
        return "J" # FINE
    
    if "FILING" in detail:
        return "K" # FILING
    if "COURT COSTS" in detail:
        return "K" # FILING
    if "TRAFFIC/SIMP MISD APPEAL FEES" in detail:
        return "K" # FILING
    if "OTHER SIMPLE MISDEMEANORS" in detail:
        return "K" # FILING

    if "INDIGENT DEFENSE" in detail:
        return "L" # INDIGENT DEFENSE

    if "SURCHARGE" in detail:
        return "M" # SURCHARGE

    if "RESTITUTION" in detail:
        return "O" # RESTITUTION

    if "THIRD PARTY" in detail:
        return "P" # THIRD PARTY

    if "ROOM/BOARD" in detail:
        return "N" # JAIL / ROOM & BOARD

    if "SHERIFF" in detail:
        return "Q" # SHERIFF

    return "R" # MISC

def process_financials(case, worksheet, row):
    financials = {}
    col = None
    for f in case['financials']:
        if f['amount'] is None:
            f['amount'] = '0'
        if not f['detail'].strip():
            financials[col] -= Decimal(f['paid'])
            continue
        col = get_finance_column(f['detail'])
        if col not in financials:
            financials[col] = Decimal(0)
        financials[col] += Decimal(f['amount'])
        financials[col] -= Decimal(f['paid'])

    for f in financials:
        worksheet[f + row] = financials[f]

def process_case(case, worksheet, row):
    i = str(row)
    worksheet['A' + i] = case['id']
    worksheet['B' + i] = case['county']

    charge = get_primary_charge(case['charges'])
    if charge is None:
        return
    
    #worksheet['C' + i] = charge['offenseDate']
    worksheet['D' + i] = charge['dispositionDate']
    worksheet['E' + i] = charge['description']
    worksheet['G' + i] = charge['code']

    process_financials(case, worksheet, i)