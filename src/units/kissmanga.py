from http.cookiejar import CookieJar, Cookie
import time
from datetime import datetime
import sqlite3
import os
import hashlib

from apscheduler.triggers.interval import IntervalTrigger
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import WebDriverException
import requests
from bs4 import BeautifulSoup

from bunbunmaru import Feed, RSSItem


manga = [
    'Shokugeki-no-Soma',
    'Komi-san-wa-Komyushou-Desu',
]

sqlite_db = os.path.join(os.path.dirname(__file__), 'kissmanga.db')

sql = {
    'create_tables': 'CREATE TABLE manga (mname TEXT, url_hash TEXT, PRIMARY KEY (mname, url_hash));',
    'check_url': 'SELECT 1 FROM manga WHERE mname = ? AND url_hash = ?;',
    'add_url': 'INSERT INTO manga (mname, url_hash) VALUES (?, ?);'
}


class KissmangaFeed(Feed):
    def __init__(self):
        super().__init__()
        self.cookies = CookieJar()
        self.headers = {}
        self.NAME = 'Kissmanga'
        self.TITLE = 'Kissmanga'
        self.LINK = 'http://kissmanga.com'
        self.DESCRIPTION = 'Anton\'s manga feed'
        self.LANGUAGE = 'ja-US'
        self.COPYRIGHT = 'lol sure'
        self.IMAGE = 'http://safebooru.org//images/2413/3a64a624c773adaea45afc9ee883d08d764c3336.png?2513303'

        self._validate()

    def get_schedule(self) -> IntervalTrigger:
        return IntervalTrigger(hours=9, jitter=60*60*3)

    def run(self) -> [RSSItem]:
        self.synchronize_cookies()

        results = []
        for title in manga:
            results.extend(self.grab_page(title))

        return results

    def grab_page(self, title: str) -> [RSSItem]:
        results = []

        url = 'http://kissmanga.com/Manga/{}'.format(title)

        r = requests.get(url, cookies=self.cookies, headers=self.headers)
        if r.status_code != 200:
            results.append(failed_scraper(url))

        soup = BeautifulSoup(r.text, 'lxml')
        links = soup.find_all(lambda tag: tag.name == 'a' and tag['href'].startswith('/Manga/{}/'.format(title)))

        urls = [link['href'] for link in links]
        already_seen = check_urls(title, urls)

        new_links = []
        new_urls = []
        for link, url, seen in zip(links, urls, already_seen):
            if not seen:
                new_links.append(link)
                new_urls.append(url)

        for link in new_links:
            results.append(RSSItem(
                title='{} - New Chapter'.format(title),
                description=link['title'],
                link='http://kissmanga.com/{}'.format(link['href']),
                author='Shameimaru Aya',
                category=title,
            ))

        insert_urls(title, new_urls)

        return results

    def synchronize_cookies(self):
        resp = requests.get('http://www.kissmanga.com', cookies=self.cookies)
        if resp.status_code == 503:
            driver = webdriver.Remote(
                command_executor='http://selenium:4444/wd/hub',
                desired_capabilities=DesiredCapabilities.HTMLUNITWITHJS
            )
            driver.get('http://www.kissmanga.com')
            time.sleep(5)
            try:
                driver.get('http://www.kissmanga.com')
            except WebDriverException:
                pass

            driver_cookies = driver.get_cookies()
            driver_agent = driver.execute_script("return navigator.userAgent")

            driver.close()

            for cookie in driver_cookies:
                ck = Cookie(
                    name=cookie['name'],
                    value=cookie['value'],
                    domain=cookie['domain'],
                    path=cookie['path'],
                    secure=cookie['secure'],
                    rest=False,
                    version=0,
                    port=None,
                    port_specified=False,
                    domain_specified=False,
                    domain_initial_dot=False,
                    path_specified=True,
                    expires=cookie['expiry'] if 'expiry' in cookie else 12 * 30 * 24 * 60 * 60,
                    discard=True,
                    comment=None,
                    comment_url=None,
                    rfc2109=False
                )
                self.cookies.set_cookie(ck)

            self.headers = {'User-Agent': driver_agent}


def check_urls(name, urls) -> [bool]:
    conn = get_db_connection()
    cur = conn.cursor()

    results = []
    params = []
    for url in urls:
        m = hashlib.md5()
        m.update(url.encode('utf-8'))
        cur.execute(sql['check_url'], (name, m.hexdigest()))
        res = cur.fetchone()
        results.append(bool(res))

    cur.close()
    conn.close()

    return [bool(r) for r in results]


def insert_urls(name, urls):
    conn = get_db_connection()
    cur = conn.cursor()

    params = []
    for url in urls:
        m = hashlib.md5()
        m.update(url.encode('utf-8'))
        params.append((name, m.hexdigest()))

    cur.executemany(sql['add_url'], params)
    cur.close()
    conn.commit()
    conn.close()


def get_db_connection():
    if os.path.isfile(sqlite_db):
        conn = sqlite3.connect(sqlite_db)
    else:
        conn = sqlite3.connect(sqlite_db)
        cur = conn.cursor()
        cur.execute(sql['create_tables'])
        cur.close()
        conn.commit()
    return conn


def failed_scraper(url: str) -> RSSItem:
    event = {
        'title': 'Scraper Failed',
        'description': 'At {time} the scraper failed to get the url {url}'.format(
            time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            url=url,
        ),
        'author': 'Shameimaru Aya',
    }
    return RSSItem(**event)
