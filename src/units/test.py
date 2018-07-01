from __future__ import absolute_import

from apscheduler.triggers.interval import IntervalTrigger

from bunbunmaru import RSSItem, Feed


class TestFeed(Feed):
    def __init__(self):
        super().__init__()
        self.NAME = 'Test'
        self.TITLE = 'Test Feed'
        self.DESCRIPTION = (
            'This is a test of the Bunbunmaru collector system. \n'
            'It increments a counter every hour.'
        )
        self.LANGUAGE = 'en-US'
        self.MANAGING_EDITOR = 'Shameimaru Aya'
        self.TTL = 3600
        self.IMAGE = 'https://simg3.gelbooru.com//samples/7d/7d/sample_7d7ded71659d3f25de110f4cbb336c1c.jpg'

        self.counter = 0
        self._validate()

    def get_schedule(self) -> IntervalTrigger:
        return IntervalTrigger(minutes=10)

    def run(self):
        event = {
            'title': 'Test unit',
            'description': 'counter is at ' + str(self.counter),
            'author': 'Shameimaru Aya',
        }
        self.counter += 1

        return [RSSItem(**event)]
