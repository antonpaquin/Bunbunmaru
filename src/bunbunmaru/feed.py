import logging

from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.interval import IntervalTrigger

from .rss import RSSItem


class RSSInvalidFeed(Exception):
    def __init__(self, message):
        super().__init__(message)
        logging.error('Error in creating feed: {}'.format(message))


class Feed:
    def __init__(self):
        logging.info('Instantiating new feed of type {}'.format(type(self).__name__))

        self.NAME = 'default'
        self.TITLE = 'Default Title'
        self.LINK = 'http://www.example.com'
        self.DESCRIPTION = 'Default Description'
        self.LANGUAGE = None
        self.COPYRIGHT = None
        self.MANAGING_EDITOR = None
        self.WEB_MASTER = None
        self.CATEGORY = {
            'content': None,
            'domain': None,
        }
        self.TTL = None
        self.IMAGE = {
            'url': None,
            'title': None,
            'link': None,
            'width': None,
            'height': None,
        }

    def _validate(self):
        logging.info('Beginning validation of feed of type {}'.format(type(self).__name__))

        try:
            assert type(self.NAME) == str
        except Exception:
            raise RSSInvalidFeed('\'name\' must be a string')

        try:
            assert type(self.TITLE) == str
        except Exception:
            raise RSSInvalidFeed('\'title\' must be a string')

        try:
            assert type(self.LINK) == str
        except Exception:
            raise RSSInvalidFeed('\'link\' must be a string')

        try:
            assert type(self.DESCRIPTION) == str
        except Exception:
            raise RSSInvalidFeed('\'description\' must be a string')

        if self.LANGUAGE is not None:
            try:
                assert type(self.LANGUAGE) == str
            except Exception:
                raise RSSInvalidFeed('\'language\' must be a string')

        if self.COPYRIGHT is not None:
            try:
                assert type(self.COPYRIGHT) == str
            except Exception:
                raise RSSInvalidFeed('\'copyright\' must be a string')

        if self.MANAGING_EDITOR is not None:
            try:
                assert type(self.MANAGING_EDITOR) == str
            except Exception:
                raise RSSInvalidFeed('\'managing_editor\' must be a string')

        if self.WEB_MASTER is not None:
            try:
                assert type(self.WEB_MASTER) == str
            except Exception:
                raise RSSInvalidFeed('\'web_master\' must be a string')

        try:
            if type(self.CATEGORY) == str:
                self.CATEGORY = {
                    'content': self.CATEGORY,
                    'domain': None,
                }
            assert type(self.CATEGORY) == dict
            if self.CATEGORY['content'] is not None:
                assert type(self.CATEGORY['content']) == str
            if self.CATEGORY['domain'] is not None:
                assert type(self.CATEGORY['domain']) == str
        except Exception:
            raise RSSInvalidFeed('\'category\' must be a string or a dict of the form: ' + str(
                {
                    'content': '<Category>',
                    'domain': '(optional) \"identifies category taxonomy\"',
                }
            ))

        if self.TTL is not None:
            try:
                assert type(self.TTL) == int
            except Exception:
                raise RSSInvalidFeed('\'ttl\' must be a datetime')

        try:
            if self.IMAGE is None:
                self.IMAGE = {
                    'url': None,
                    'title': None,
                    'link': None,
                }
            if type(self.IMAGE) == str:
                self.IMAGE = {
                    'url': self.IMAGE,
                    'title': self.TITLE,
                    'link': self.LINK,
                }
            assert type(self.IMAGE) == dict
            assert type(self.IMAGE['url']) in {type(None), str}
            assert type(self.IMAGE['title']) in {type(None), str}
            assert type(self.IMAGE['link']) in {type(None), str}
            if 'width' in self.IMAGE:
                assert type(self.IMAGE['width']) in {type(None), int}
            else:
                self.IMAGE['width'] = None
            if 'height' in self.IMAGE:
                assert type(self.IMAGE['height']) in {type(None), int}
            else:
                self.IMAGE['height'] = None
        except Exception:
            raise RSSInvalidFeed('\'image\' must be a string or a dict of the form: ' + str(
                {
                    'url': '<link to image>',
                    'title': '<alt text for image>',
                    'link': '<link to the site containing the image>',
                    'width': '(optional) the width of the image',
                    'height': '(optional) the height of the image',
                }
            ))

    def get_schedule(self) -> BaseTrigger:
        return IntervalTrigger(minutes=15)

    def run(self) -> [RSSItem]:
        return []

    def __repr__(self):
        import json
        return json.dumps(
            {
                'NAME': self.NAME,
                'TITLE': self.TITLE,
                'LINK': self.LINK,
                'DESCRIPTION': self.DESCRIPTION,
                'LANGUAGE': self.LANGUAGE,
                'COPYRIGHT': self.COPYRIGHT,
                'MANAGING_EDITOR': self.MANAGING_EDITOR,
                'WEB_MASTER': self.WEB_MASTER,
                'CATEGORY': self.CATEGORY,
                'TTL': self.TTL,
                'IMAGE': self.IMAGE,
            },
            indent=4,
            sort_keys=True,
        )
