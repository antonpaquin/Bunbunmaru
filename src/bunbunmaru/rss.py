from datetime import datetime
import logging
import uuid


class RSSInvalidItem(Exception):
    def __init__(self, message):
        super().__init__(message)
        logging.error('Error in creating RSSItem: {}'.format(message))
    pass


class RSSItem:

    class AUTO:
        pass

    def __init__(
            self,
            title=None,
            link=None,
            description=None,
            author=None,
            category=None,
            comments_url=None,
            enclosure=None,
            guid=AUTO,
            pub_date=AUTO,
            source=None,
    ):
        if guid == RSSItem.AUTO:
            self.guid = {
                'content': str(uuid.uuid4()),
            }
        elif type(guid) == str:
            self.guid = {
                'content': guid,
            }
        else:
            self.guid = guid

        if pub_date == RSSItem.AUTO:
            self.pub_date = datetime.now()
        else:
            self.pub_date = pub_date

        if type(category) == str:
            self.category = {
                'content': category,
            }
        else:
            self.category = category

        self.title = title
        self.link = link
        self.description = description
        self.author = author
        self.comments_url = comments_url
        self.enclosure = enclosure
        self.source = source

        self._validate()

    def _validate(self):
        if self.source:
            try:
                assert type(self.source) == dict
                assert type(self.source['content']) == str
                assert type(self.source['url']) == str
            except Exception:
                raise RSSInvalidItem('\'source\' must be a dict of the form: ' + str(
                    {
                        'content': '<RSS source name>',
                        'url': '<RSS source url>',
                    }
                ))
        else:
            self.source = {
                'content': None,
                'url': None,
            }

        if self.enclosure:
            try:
                assert type(self.enclosure) == dict
                assert type(self.enclosure['url']) == str
                assert type(self.enclosure['mime']) == str
                if 'length' not in self.enclosure:
                    self.enclosure['length'] = 0
                assert type(self.enclosure['length']) == int
            except Exception:
                raise RSSInvalidItem('\'enclosure\' must be a dict of the form: ' + str(
                    {
                        'url': '<content url>',
                        'mime': '<content mime type>',
                        'length': '(optional) <content length in bytes>',
                    }
                ))
        else:
            self.enclosure = {
                'url': None,
                'mime': None,
                'length': None,
            }

        if self.category:
            try:
                assert type(self.category) == dict
                assert type(self.category['content']) == str
                if 'domain' in self.category:
                    assert type(self.category['domain']) == str
                else:
                    self.category['domain'] = None
            except Exception:
                raise RSSInvalidItem('\'category\' must be a string or a dict of the form: ' + str(
                    {
                        'content': '<Category>',
                        'domain': '(optional) \"identifies category taxonomy\"',
                    }
                ))
        else:
            self.category = {
                'content': None,
                'domain': None,
            }

        if self.pub_date:
            try:
                assert type(self.pub_date) == datetime
            except Exception:
                raise RSSInvalidItem('\'pub_date\' must be a datetime')

        if self.guid:
            try:
                assert type(self.guid) == dict
                assert type(self.guid['content']) == str
                if 'is_permalink' in self.guid:
                    assert type(self.guid['is_permalink']) == bool
                else:
                    self.guid['is_permalink'] = False
            except Exception:
                raise RSSInvalidItem('\'guid\' must be a string or a dict of the form: ' + str(
                    {
                        'content': '<guid>',
                        'is_permalink': '(optional) true if content is a permalink to the item',
                    }
                ))
        else:
            self.guid = {
                'content': None,
                'is_permalink': None,
            }

        if self.comments_url:
            try:
                assert type(self.comments_url) == str
            except Exception:
                raise RSSInvalidItem('\'comments_url\' must be a string')

        if self.author:
            try:
                assert type(self.author) == str
            except Exception:
                raise RSSInvalidItem('\'author\' must be a string')

        if self.link:
            try:
                assert type(self.link) == str
            except Exception:
                raise RSSInvalidItem('\'link\' must be a string')

        if self.description:
            try:
                assert type(self.description) == str
            except Exception:
                raise RSSInvalidItem('\'description\' must be a string')

        if self.title:
            try:
                assert type(self.title) == str
            except Exception:
                raise RSSInvalidItem('\'title\' must be a string')

        try:
            assert self.title or self.description
        except Exception:
            raise RSSInvalidItem('Either \'title\' or \'description\' must be set')

    def __repr__(self):
        import json
        return json.dumps(
            {
                'title': self.title,
                'link': self.link,
                'description': self.description,
                'author': self.author,
                'category': self.category,
                'comments_url': self.comments_url,
                'enclosure': self.enclosure,
                'guid': self.guid,
                'pub_date': self.pub_date.strftime('%Y-%m-%d %H:%M:%S'),
                'source': self.source,
            },
            indent=4,
            sort_keys=True,
        )
