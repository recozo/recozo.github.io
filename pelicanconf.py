#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Recozo'
SITENAME = "Recozo's Blog"
SITEURL = ''

PATH = 'content'

# https://github.com/alexandrevicenzi/Flex/wiki
THEME = './.venv/lib/python3.10/site-packages/pelican/themes/Flex'

PORT = 10001

TIMEZONE = 'Asia/Shanghai'
DEFAULT_DATE = 'fs'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

# http://code.nabla.net/doc/docutils/api/docutils/docutils.languages.html
DEFAULT_LANG = 'zh-cn'

ARTICLE_ORDER_BY = 'reversed-modified'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# https://github.com/alexandrevicenzi/Flex/wiki/Code-Highlight
# https://docs.getpelican.com/en/latest/content.html#syntax-highlighting
PYGMENTS_STYLE = "default"
MAIN_MENU = True
LINKS = (
    ("Portfolio", "http://www.github.com"),
)
SOCIAL = (
    ("linkedin", "https://www.linkedin.com/in/alexandrevicenzi/en"),
    ("github", "https://github.com/alexandrevicenzi"),
    ("twitter", "https://twitter.com/alxvicenzi"),
)
MENUITEMS = (
    ("Archives", "/archives.html"),
    ("Categories", "/categories.html"),
    ("Tags", "/tags.html"),
)