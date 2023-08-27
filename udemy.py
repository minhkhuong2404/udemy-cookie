import json
import threading
import time

import cloudscraper
import requests
import browser_cookie3


class LoginException(Exception):
    """Login Error

    Args:
        Exception (str): Exception Reason
    """

    pass


class RaisingThread(threading.Thread):
    def run(self):
        self._exc = None
        try:
            super().run()
        except Exception as e:
            self._exc = e

    def join(self, timeout=None):
        super().join(timeout=timeout)
        if self._exc:
            raise self._exc


class Udemy:
    def __init__(self, interface: str):
        self.interface = interface
        self.client = cloudscraper.CloudScraper()
        self.user_agent = "okhttp/4.9.2 UdemyAndroid 8.9.2(499) (phone)"

    def make_cookies(self, client_id: str, access_token: str, csrf_token: str):
        self.cookie_dict = dict(
            client_id=client_id,
            access_token=access_token,
            csrf_token=csrf_token,
        )

    def fetch_cookies(self):
        """Gets cookies from browser
        Sets cookies_dict, cookie_jar
        """
        cookies = browser_cookie3.load(domain_name="www.udemy.com")
        self.cookie_dict: dict = requests.utils.dict_from_cookiejar(cookies)
        self.cookie_jar = cookies

    def manual_login(self, email: str, password: str):

        # s = cloudscraper.CloudScraper()

        s = requests.session()
        r = s.get(
            "https://www.udemy.com/join/signup-popup/",
            headers={"User-Agent": self.user_agent},
        )

        csrf_token = r.cookies["csrftoken"]

        data = {
            "csrfmiddlewaretoken": csrf_token,
            "locale": "en_US",
            "email": email,
            "password": password,
        }

        # ss = requests.session()
        s.cookies.update(r.cookies)
        s.headers.update(
            {
                "User-Agent": self.user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-GB,en;q=0.5",
                "Referer": "https://www.udemy.com/join/login-popup/?locale=en_US&response_type=html&next=https%3A%2F%2Fwww.udemy.com%2F",
                "Origin": "https://www.udemy.com",
                "DNT": "1",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
            }
        )
        # r = s.get("https://www.udemy.com/join/login-popup/?response_type=json")
        s = cloudscraper.create_scraper(sess=s)
        r = s.post(
            "https://www.udemy.com/join/login-popup/?response_type=json",
            data=data,
            allow_redirects=False,
        )
        if r.text.__contains__("returnUrl"):
            self.make_cookies(
                r.cookies["client_id"], r.cookies["access_token"], csrf_token
            )
        else:
            login_error = r.json()["error"]["data"]["formErrors"][0]
            if login_error[0] == "Y":
                raise LoginException("Too many logins per hour try later")
            elif login_error[0] == "T":
                raise LoginException("Email or password incorrect")
            else:
                raise LoginException(login_error)

    def get_session_info(self):
        """Get Session info
        Sets Client Session, currency and name
        """
        s = cloudscraper.CloudScraper()

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-GB,en;q=0.5",
            "Referer": "https://www.udemy.com/",
            "X-Requested-With": "XMLHttpRequest",
            "DNT": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }

        r = s.get(
            "https://www.udemy.com/api-2.0/contexts/me/?header=True",
            cookies=self.cookie_dict,
            headers=headers,
        )
        r = r.json()
        if r["header"]["isLoggedIn"] == False:
            raise LoginException("Login Failed")

        self.display_name: str = r["header"]["user"]["display_name"]
        r = s.get(
            "https://www.udemy.com/api-2.0/shopping-carts/me/",
            headers=headers,
            cookies=self.cookie_dict,
        )
        r = r.json()
        self.currency: str = r["user"]["credit"]["currency_code"]

        s = cloudscraper.CloudScraper()
        s.cookies.update(self.cookie_dict)
        s.headers.update(headers)
        s.keep_alive = False
        self.client = s

    def export_cookie_to_file(self):
        """Exports cookies to file
        """
        url = ('https://www.udemy.com/api-2.0/users/me/subscribed-courses/?ordering=-last_accessed&fields['
               'course]=archive_time,buyable_object_type,completion_ratio,enrollment_time,favorite_time,features,'
               'image_240x135,image_480x270,is_practice_test_course,is_private,is_published,last_accessed_time,'
               'num_collections,published_title,title,tracking_id,url,visible_instructors&fields[user]=@min,'
               'job_title&page=1&page_size=12&is_archived=false')
        x = cloudscraper.create_scraper().get(url, headers={"User-Agent": self.user_agent})
        cookies_www_udemy = browser_cookie3.chrome(domain_name="www.udemy.com")
        cookies_udemy = browser_cookie3.chrome(domain_name=".udemy.com")

        print(x.cookies.get_dict())

        cj = browser_cookie3.chrome(domain_name="www.udemy.com")
        cjw = browser_cookie3.chrome(domain_name=".udemy.com")

        with open('cookies_www_udemy.json', 'w') as f:
            json.dump(requests.utils.dict_from_cookiejar(cookies_www_udemy), f)

        with open('cookies_udemy.json', 'w') as f:
            json.dump(requests.utils.dict_from_cookiejar(cookies_udemy), f)

    def convertCookieFileToAnotherFormat(self):
        # time when the first cookie is created
        standard_time = 1693121752
        current_time = time.time()
        # convert cookies_www_udemy.json to j2team_cookies.json
        # each field in cookies_www_udemy.json is a name field in j2team_cookies.json
        # each value of the field in cookies_www_udemy.json is a value field in j2team_cookies.json
        # for other fields in j2team_cookies.json, use default value
        with open('cookies_udemy.json', 'r') as f:
            cookies_www_udemy = json.load(f)
        with open('j2team_cookies_default.json', 'r') as f:
            j2team_cookies = json.load(f)

        print(cookies_www_udemy)
        list_cookies = j2team_cookies['cookies']
        print(list_cookies)

        for cookie in cookies_www_udemy:
            # find cookie in list_cookies where name = cookie
            # update value of cookie in list_cookies
            for i in range(len(list_cookies)):
                if list_cookies[i]['name'] == cookie:
                    list_cookies[i]['value'] = cookies_www_udemy[cookie]
                    # add more time for expirationDate
                    try:
                        list_cookies[i]['expirationDate'] = list_cookies[i]['expirationDate'] + (current_time - standard_time)
                    except KeyError as e:
                        print(e)
                    break

        with open('j2team_cookies.json', 'w') as f:
            json.dump(j2team_cookies, f)
