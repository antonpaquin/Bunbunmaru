from __future__ import absolute_import

from datetime import datetime

from apscheduler.triggers.cron import CronTrigger

from bunbunmaru import RSSItem, Feed


class AnkiFeed(Feed):
    def __init__(self):
        super().__init__()

        self.NAME = 'anki'
        self.TITLE = 'Anki Reminders'
        self.DESCRIPTION = 'Daily anki reminders'
        self.LANGUAGE = 'en-US'
        self.MANAGING_EDITOR = 'Shameimaru Aya'
        self.TTL = 60*60*24
        self.IMAGE = 'https://djtguide.neocities.org/assets/image01.png'
        self._validate()

    def get_schedule(self) -> CronTrigger:
        return CronTrigger(hour=9)

    def run(self) -> [RSSItem]:
        event = {
            'title': 'Anki Reminder',
            'description': 'Autogenerated ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'author': 'Shameimaru Aya',
            'enclosure': {
                'url': 'https://djtguide.neocities.org/assets/image01.png',
                'mime': 'image/png',
                'length': 137772,
            },
        }

        return [RSSItem(**event)]
