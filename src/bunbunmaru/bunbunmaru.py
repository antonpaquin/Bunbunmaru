from threading import Thread
import os
import sqlite3
import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from utils import load_sql

from .feed import Feed
from .rss import RSSItem


logging.basicConfig(
    filename='bunbunmaru_collector.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


sql = load_sql(os.path.join(os.path.dirname(__file__), 'sql'))


class Bunbunmaru:
    _instance = None

    def __init__(self, db_name):
        logging.info('INITIALIZING COLLECTOR')
        self._units = {}
        self._running = False
        self._scheduler = BlockingScheduler({
            'apscheduler.jobstores.default': {
                'type': 'sqlalchemy',
                'url': 'sqlite:////data/scheduler.db'
            }
        })
        self._db_name = db_name
        Bunbunmaru._instance = self

    def add_unit(self, unit: Feed):
        assert isinstance(unit, Feed), 'Unit must inherit from bunbunmaru.Feed'
        logging.info('Adding unit {}'.format(unit.NAME))
        self._units[unit.NAME] = unit
        if self._running:
            self._schedule_unit(unit)

    def run(self):
        logging.info('Starting scheduling')
        for _, unit in self._units.items():
            self._schedule_unit(unit)
        self._running = True
        logging.info('All units scheduled')
        self._scheduler.start()

    def fork(self):
        t = Thread(target=self.run)
        t.start()
        logging.info('Run process forked')

    def _schedule_unit(self, unit: Feed):
        logging.info('Scheduling unit {}'.format(unit.NAME))
        trigger = unit.get_schedule()
        self._scheduler.add_job(
            func=self._run_unit,
            kwargs={'name': unit.NAME},
            trigger=trigger,
            id=unit.NAME,
            name=unit.NAME,
            coalesce=True,
            next_run_time=datetime.now(),
            replace_existing=True,
        )

    @staticmethod
    def _run_unit(name: str):
        self = Bunbunmaru._instance
        unit = self._units.get(name, None)
        if unit:
            response = unit.run()
            self._process_items(response, unit)
        else:
            # If it gets here, here's what's going on:
            # The scheduler serialized this unit to run, then died and was restarted
            # On the restart, the unit was added to this module with another name or not at all
            # To fix, either unschedule it (self._scheduler.remove_job(name)) or just swallow the error
            logging.error('Unit {} could not be run: not found'.format(name))

    def _process_items(self, items: [RSSItem], unit: Feed):
        logging.info('Received a batch of events from unit {}'.format(unit.NAME))
        assert isinstance(items, (set, list, tuple)), 'run() must return an array of bunbunmaru.RSSItem'
        for item in items:
            assert isinstance(item, RSSItem), 'run() must return an array of bunbunmaru.RSSItem'

        feed_id = self._ensure_feed(unit)

        for item in items:
            self._insert_rssitem(feed_id, item)

    def _ensure_feed(self, unit: Feed):
        conn = self._get_db_connection()
        cur = conn.cursor()

        cur.execute(sql['select_feed_id'], (unit.NAME,))
        feed_id = cur.fetchone()

        if not feed_id:
            logging.info('Requested feed {} does not exist, creating...'.format(unit.NAME))
            cur.execute(
                sql['insert_feed'],
                (
                    unit.NAME, unit.TITLE, unit.LINK, unit.DESCRIPTION, unit.LANGUAGE, unit.COPYRIGHT,
                    unit.MANAGING_EDITOR, unit.WEB_MASTER, unit.CATEGORY['content'], unit.CATEGORY['domain'], unit.TTL,
                    unit.IMAGE['url'], unit.IMAGE['title'], unit.IMAGE['link'], unit.IMAGE['width'],
                    unit.IMAGE['height'],
                )
            )
            cur.execute(sql['select_feed_id'], (unit.NAME,))
            feed_id = cur.fetchone()

        feed_id = feed_id[0]
        conn.commit()
        return feed_id

    def _insert_rssitem(self, feed_id: int, item: RSSItem):
        conn = self._get_db_connection()
        cur = conn.cursor()

        cur.execute(
            sql['insert_rss_item'],
            (
                feed_id, item.title, item.link, item.description, item.author, item.comments_url, item.guid['content'],
                item.guid['is_permalink'], item.pub_date, item.category['content'], item.category['domain'],
                item.enclosure['url'], item.enclosure['mime'], item.enclosure['length'], item.source['content'],
                item.source['url'],
            )
        )
        conn.commit()

    def _get_db_connection(self):
        if os.path.isfile(self._db_name):
            conn = sqlite3.connect(self._db_name)
        else:
            logging.info('Database does not exist, initializing...')
            conn = sqlite3.connect(self._db_name)
            cur = conn.cursor()
            cur.execute(sql['create_items'])
            cur.execute(sql['create_feeds'])
            conn.commit()
        return conn
