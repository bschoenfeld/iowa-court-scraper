import requests
import time
import functools
import http.client
import logging
import http

BASE_URL = "https://www.iowacourts.state.ia.us/ESAWebApp/"
USER_AGENT = u"Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; " + \
    u"rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11"

def build_url(path):
    return BASE_URL + path


class Reader:
    def __init__(self):
        # HTTP Logging for requests → logs/http.log
        http_log = logging.getLogger('http')
        def _httpclient_log(*args):
            """ callback used by http"""
            if args[0] == 'reply:':
                http_log.info('===== response =====')
            args = [_format_http_arg(arg) for arg in args[1:]]
            http_log.info(" ".join(args))

        def _format_http_arg(arg):
            """ bunch of weird reformatting for logs from http"""
            if arg[:2] == "b'":
                arg = arg[2:-1]
            if arg[:1] == "'" and arg[-1:]:
                arg = arg[1:-1]
            if arg[-2:] == '\\r\\n':
                arg = arg[:-2]
            # http_logger.info(arg)
            if arg[:4].strip() in ('GET', 'POST'):
                # breaking up HTTP headers
                arg = arg.split('\\r\\n')
                arg = '\n'.join(arg[:-2])
            return arg

        http.client.print = _httpclient_log
        http.client.HTTPConnection.debuglevel = 1

        self.http_log = http_log
        self.requests = requests.session()
        self.requests.headers['User-Agent'] = USER_AGENT

    def api_call(func):
        @functools.wraps(func)
        def _logWrapper(self, *args, **kwargs):
            try:
                start = time.time()
                self.http_log.info(f'===== request:{func.__name__} =====')
                result = func(self, *args, **kwargs)

                elapsed = time.time() - start
                self.http_log.info(f'Elapsed: {elapsed}')
                self.http_log.info(f'HTTP {result.status_code}')
                if result.status_code != 200:
                    self.http_log.error('Error while executing HTTP request:')
                    self.http_log.error(result.text)
                return result.text

            except requests.RequestException as ex:
                logging.error(ex)
                return ""

        return _logWrapper

    def check_session(self):
        result = self.load_adv()
        return result != ''

    @api_call
    def init(self):
        url = build_url("ESALogin.jsp")
        return self.requests.get(url)

    @api_call
    def load_adv(self):
        url = build_url("TrialAdvFrame")
        return self.requests.get(url)

    def get_cookies(self):
        return self.requests.cookies.get_dict()

    def set_cookies(self, cookies):
        for name, value in cookies.items():
            self.requests.cookies.set(name, value)

    @api_call
    def login(self, username, password):
        url = build_url("EUACustomLoginServlet")
        data = {
            'userid': username,
            'password': password,
            'agency': "JUDICIAL",
            'jumpto': build_url("TrialCourtStateWide"),
            'search': "Logon"
        }
        return self.requests.post(url, params=data)

    @api_call
    def logoff(self):
        url = build_url("EPALogout")
        data = {
            'logoffButton': 'Logoff'
        }
        return self.requests.post(url, params=data)

    @api_call
    def search(self, firstname, middlename, lastname):
        url = build_url("TrialCaseSearchResultServlet")
        data = {
            'searchtype': 'N',
            'last': lastname,
            'first': firstname,
            'middle': middlename,
            'alast': '',
            'afirst': '',
            'amiddle': '',
            'role': "ALL",
            'and/or': '',
            'county': "00",
            'casetype': "ALL",
            'caseid1sel': "",
            'caseid3sel': "AM",
            'caseid1': "",
            'caseid2': "",
            'caseid3': "",
            'caseid4': "",
            'citation_number': "",
            'search': "Search"
        }
        return self.requests.post(url, data=data)

    @api_call
    def case_summary(self, case_id):
        url = build_url("TViewCaseCivil?caseid=")
        url += case_id.replace(" ", "+")
        return self.requests.get(url)

    @api_call
    def case_charges(self):
        url = build_url("TViewCharges")
        return self.requests.get(url)

    @api_call
    def case_financials(self):
        url = build_url("TViewFinancials")
        return self.requests.get(url)


