import sqlite3
import os
from datetime import datetime

from flask import Flask
from lxml import etree
from utils import load_sql


sql = load_sql(os.path.join(os.path.dirname(__file__), 'sql'))
db_name = None


app = Flask(__name__)


@app.route('/')
def list_feeds():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql['list_feeds'])
    feeds = cur.fetchall()

    root = etree.Element('html')
    for feed_id, name in feeds:
        item = etree.Element('a')
        item.text = name
        item.set('href', '/feed/' + str(feed_id))
        root.append(item)
        br = etree.Element('br')
        root.append(br)

    return '<!DOCTYPE html>' + etree.tostring(root).decode()


@app.route('/feed/<int:feed_id>')
def get_feed(feed_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(sql['get_feed'], (feed_id,))
    feed = cur.fetchone()

    cur.execute(sql['get_latest'], (feed_id,))
    items = cur.fetchall()

    rss = build_feed(feed, items)
    content = '<?xml version="1.0" encoding="utf-8"?>\n' + etree.tostring(rss).decode()
    headers = {
        'Content-Type': 'text/xml'
    }

    return content, 200, headers


def build_feed(feed, items):
    root = etree.Element('rss')
    root.set('version', '2.0')

    channel = build_channel(*feed)

    for idata in items:
        item = build_item(*idata)
        channel.append(item)

    root.append(channel)

    return root


def build_channel(name, title, link, description, language, copyright, managing_editor, web_master, category,
                  category_domain, ttl, image_url, image_title, image_link, image_width, image_height):
    channel = etree.Element('channel')

    e_title = etree.Element('title')
    e_title.text = title
    channel.append(e_title)

    e_link = etree.Element('link')
    e_link.text = link
    channel.append(e_link)

    e_description = etree.Element('description')
    e_description.text = description
    channel.append(e_description)

    if language:
        e_language = etree.Element('language')
        e_language.text = language
        channel.append(e_language)

    if copyright:
        e_copyright = etree.Element('copyright')
        e_copyright.text = copyright
        channel.append(e_copyright)

    if managing_editor:
        e_managing_editor = etree.Element('managingEditor')
        e_managing_editor.text = managing_editor
        channel.append(e_managing_editor)

    if web_master:
        e_web_master = etree.Element('webMaster')
        e_web_master.text = web_master
        channel.append(e_web_master)

    if category:
        e_category = etree.Element('category')
        e_category.text = category
        if category_domain:
            category.set('domain', category_domain)
        channel.append(e_category)

    if ttl:
        e_ttl = etree.Element('ttl')
        e_ttl.text = str(ttl)
        channel.append(e_ttl)

    if image_url:
        e_image = etree.Element('image')

        e_image_url = etree.Element('url')
        e_image_url.text = image_url
        e_image.append(e_image_url)

        e_image_title = etree.Element('title')
        e_image_title.text = image_title
        e_image.append(e_image_title)

        e_image_link = etree.Element('link')
        e_image_link.text = image_link
        e_image.append(e_image_link)

        if image_width:
            e_image_width = etree.Element('width')
            e_image_width.text = image_width
            e_image.append(e_image_width)

        if image_height:
            e_image_height = etree.Element('height')
            e_image_height.text = image_height
            e_image.append(e_image_height)

        channel.append(e_image)

    e_last_build = etree.Element('lastBuildDate')
    e_last_build.text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    channel.append(e_last_build)

    e_generator = etree.Element('generator')
    e_generator.text = 'Bunbunmaru'
    channel.append(e_generator)

    e_bunbunmaru = etree.Element('bunbunmaru')
    e_bunbunmaru_name = etree.Element('feedName')
    e_bunbunmaru_name.text = name
    e_bunbunmaru.append(e_bunbunmaru_name)
    channel.append(e_bunbunmaru)

    e_docs = etree.Element('docs')
    e_docs.text = 'https://validator.w3.org/feed/docs/rss2.html'
    channel.append(e_docs)

    return channel


def build_item(title, link, description, author, comments_url, guid, guid_is_permalink, pub_date, category,
               category_domain, enclosure_url, enclosure_mime, enclosure_length, source, source_url):
    item = etree.Element('item')

    if title:
        e_title = etree.Element('title')
        e_title.text = title
        item.append(e_title)

    if link:
        e_link = etree.Element('link')
        e_link.text = link
        item.append(e_link)

    if description:
        e_description = etree.Element('description')
        e_description.text = description
        item.append(e_description)

    if author:
        e_author = etree.Element('author')
        e_author.text = author
        item.append(e_author)

    if category:
        e_category = etree.Element('category')
        e_category.text = category
        if category_domain:
            e_category.set('domain', category_domain)
        item.append(e_category)

    if comments_url:
        e_comments = etree.Element('comments')
        e_comments.text = comments_url
        item.append(e_comments)

    if enclosure_url:
        e_enclosure = etree.Element('enclosure')
        e_enclosure.set('url', enclosure_url)
        e_enclosure.set('mime', enclosure_mime)
        e_enclosure.set('length', str(enclosure_length))
        item.append(e_enclosure)

    if guid:
        e_guid = etree.Element('guid')
        e_guid.text = guid
        if guid_is_permalink is not None:
            e_guid.set('is_permalink', str(bool(guid_is_permalink)))
        item.append(e_guid)

    if pub_date:
        e_pubdate = etree.Element('pubDate')
        e_pubdate.text = pub_date
        item.append(e_pubdate)

    if source:
        e_source = etree.Element('source')
        e_source.text = source
        if source_url:
            e_source.set('url', source_url)
        item.append(e_source)

    return item


def get_conn():
    if not db_name:
        raise NameError('Database is missing')

    if not os.path.isfile(db_name):
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        cur.execute(sql['create_items'])
        cur.execute(sql['create_feeds'])
        conn.commit()
    else:
        conn = sqlite3.connect(db_name)

    return conn


def set_db(name: str):
    global db_name
    db_name = name


def run(host, port):
    app.run(host=host, port=port)
