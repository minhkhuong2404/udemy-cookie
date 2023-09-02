import json
import os
import threading
import time

import cloudscraper
import requests
import browser_cookie3


class LoginException(Exception):
    """Raised when login fails"""


class RaisingThread(threading.Thread):
    """Thread that raises exceptions in main thread"""

    def run(self):
        self._exc = None
        try:
            super().run()
        except Exception as exception:
            self._exc = exception

    def join(self, timeout=None):
        super().join(timeout=timeout)
        if self._exc:
            raise self._exc


def convert_to_j2team_cookie():
    """ Convert cookies_www_udemy.json to j2team_cookies.json"""
    # time when the first cookie is created
    standard_time = 1693121752
    current_time = time.time()
    # convert cookies_www_udemy.json to j2team_cookies.json
    # each field in cookies_www_udemy.json is a name field in j2team_cookies.json
    # each value of the field in cookies_www_udemy.json is a value field in j2team_cookies.json
    # for other fields in j2team_cookies.json, use default value
    with open('cookies_udemy.json', 'r') as file:
        cookies_www_udemy = json.load(file)
    with open('j2team_cookies_default.json', 'r') as file:
        j2team_cookies = json.load(file)

    list_cookies = j2team_cookies['cookies']

    for cookie in cookies_www_udemy:
        # find cookie in list_cookies where name = cookie
        # update value of cookie in list_cookies
        for _, list_cookie in enumerate(list_cookies):
            if list_cookie['name'] == cookie:
                list_cookie['value'] = cookies_www_udemy[cookie]
                # add more time for expirationDate
                try:
                    list_cookie['expirationDate'] = list_cookie['expirationDate'] + (
                            current_time - standard_time)
                except KeyError as key_error:
                    print(key_error)
                break

    with open('j2team_cookies.json', 'w') as f:
        json.dump(j2team_cookies, f)


class Udemy:
    """Udemy Class"""

    def __init__(self, interface: str):
        self.cookie_jar = None
        self.cookie_dict = None
        self.interface = interface
        self.client = cloudscraper.CloudScraper()
        self.user_agent = "okhttp/4.9.2 UdemyAndroid 8.9.2(499) (phone)"

    def make_cookies(self, client_id: str, access_token: str, csrf_token: str):
        """Makes cookies from client_id, access_token, csrf_token"""
        self.cookie_dict =\
            {"client_id": client_id, "access_token": access_token, "csrf_token": csrf_token }

    def fetch_cookies(self):
        """Gets cookies from browser
        Sets cookies_dict, cookie_jar
        """
        cookies = browser_cookie3.load(domain_name="www.udemy.com")
        self.cookie_dict: dict = requests.utils.dict_from_cookiejar(cookies)
        self.cookie_jar = cookies

    def manual_login(self, email: str, password: str):
        """Manual Login"""

        # cloud_scraper = cloudscraper.CloudScraper()

        cloud_scraper = requests.session()
        cloud_scraper_response = cloud_scraper.get(
            "https://www.udemy.com/join/signup-popup/",
            headers={"User-Agent": self.user_agent},
        )

        csrf_token = cloud_scraper_response.cookies["csrftoken"]

        data = {
            "csrfmiddlewaretoken": csrf_token,
            "locale": "en_US",
            "email": email,
            "password": password,
        }

        # ss = requests.session()
        cloud_scraper.cookies.update(cloud_scraper_response.cookies)
        cloud_scraper.headers.update(
            {
                "User-Agent": self.user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-GB,en;q=0.5",
                "Referer": "https://www.udemy.com/join/login-popup/?locale=en_US&response_type=html&next=https%3A%2F"
                           "%2Fwww.udemy.com%2F",
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
        cloud_scraper = cloudscraper.create_scraper(sess=cloud_scraper)
        cloud_scraper_response = cloud_scraper.post(
            "https://www.udemy.com/join/login-popup/?response_type=json",
            data=data,
            allow_redirects=False,
        )
        if "returnUrl" in cloud_scraper_response.text:
            self.make_cookies(
                cloud_scraper_response.cookies["client_id"], cloud_scraper_response.cookies["access_token"], csrf_token
            )
        else:
            login_error = cloud_scraper_response.json()["error"]["data"]["formErrors"][0]
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
        cloud_scraper = cloudscraper.CloudScraper()

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

        cloud_scraper_response = cloud_scraper.get(
            "https://www.udemy.com/api-2.0/contexts/me/?header=True",
            cookies=self.cookie_dict,
            headers=headers,
        )
        cloud_scraper_response = cloud_scraper_response.json()
        if not cloud_scraper_response["header"]["isLoggedIn"]:
            raise LoginException("Login Failed")

        self.display_name: str = cloud_scraper_response["header"]["user"]["display_name"]
        cloud_scraper_response = cloud_scraper.get(
            "https://www.udemy.com/api-2.0/shopping-carts/me/",
            headers=headers,
            cookies=self.cookie_dict,
        )
        cloud_scraper_response = cloud_scraper_response.json()
        self.currency: str = cloud_scraper_response["user"]["credit"]["currency_code"]

        cloud_scraper = cloudscraper.CloudScraper()
        cloud_scraper.cookies.update(self.cookie_dict)
        cloud_scraper.headers.update(headers)
        cloud_scraper.keep_alive = False
        self.client = cloud_scraper

    def export_cookie_to_file(self):
        """Exports cookies to file
        """
        url = ('https://www.udemy.com/api-2.0/users/me/subscribed-courses/?ordering=-last_accessed&fields['
               'course]=archive_time,buyable_object_type,completion_ratio,enrollment_time,favorite_time,features,'
               'image_240x135,image_480x270,is_practice_test_course,is_private,is_published,last_accessed_time,'
               'num_collections,published_title,title,tracking_id,url,visible_instructors&fields[user]=@min,'
               'job_title&page=1&page_size=12&is_archived=false')
        cloudscraper.create_scraper().get(url, headers={"User-Agent": self.user_agent})
        cookies_www_udemy = browser_cookie3.chrome(domain_name="www.udemy.com")
        cookies_udemy = browser_cookie3.chrome(domain_name=".udemy.com")

        with open('cookies_www_udemy.json', 'w') as file:
            json.dump(requests.utils.dict_from_cookiejar(cookies_www_udemy), file)

        with open('cookies_udemy.json', 'w') as file:
            json.dump(requests.utils.dict_from_cookiejar(cookies_udemy), file)
