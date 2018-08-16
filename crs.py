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
