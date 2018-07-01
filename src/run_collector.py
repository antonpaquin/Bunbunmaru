from units.anki import AnkiFeed
from units.test import TestFeed
from units.kissmanga import KissmangaFeed

from bunbunmaru import Bunbunmaru

b = Bunbunmaru('bunbunmaru.db')

b.add_unit(AnkiFeed())
b.add_unit(KissmangaFeed())
b.add_unit(TestFeed())

b.run()
