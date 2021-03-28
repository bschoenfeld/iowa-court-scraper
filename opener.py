import json
import requests

user_agent = u"Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; " + \
    u"rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11"


class Opener:
    def __init__(self):
        #if os.environ.get('PROXIMO_URL', '') != '':
        #    proxy = urllib2.ProxyHandler({'http': os.environ.get('PROXIMO_URL', '')})
        #    auth = urllib2.HTTPBasicAuthHandler()
        #    self.opener = urllib2.build_opener(cookie_processor, proxy, auth, urllib2.HTTPHandler)
        #else:
        self.cookieJar = [('User-Agent', user_agent)]

    def open(self, url, **kwargs):
        """

        Parameters
        ----------
        url: string
        data: dict

        Returns
        -------

        """
        url = args[0]
        if len(args) == 2:
            data = args[1]
            return requests.get(url, cookies=self.cookieJar)
        return requests.get(url)

'''
import mechanize

class NoHistory(object):
    def add(self, *a, **k): pass
    def clear(self): pass

class Opener:
    def __init__(self):
        self.opener = mechanize.Browser(history=NoHistory())
        self.opener.set_handle_robots(False)

    def set_cookie(self, name, value):
        self.opener.set_cookie(str(name) + '=' + str(value))

    def open(self, *args):
        url = args[0]
        if len(args) == 2:
            data = args[1]
            return self.opener.open(url, data)
        return self.opener.open(url)
'''