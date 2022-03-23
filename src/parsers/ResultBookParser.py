from bs4 import BeautifulSoup
from const import HOST
from src.entities.ResultItem import ResultItem
from src.utilities.Utility import remove_prefix


class ResultBookParser:
    def __init__(self, div_gallery: BeautifulSoup):
        self.div_gallery = div_gallery

    def parse(self) -> ResultItem:
        item = ResultItem()
        item.title = self.parseTitle()
        item.url = self.parseLink()
        src = self.parse_src()
        item.token = src
        item.tumb_url = None
        item.id = self.parseId()
        return item

    def parseTitle(self):
        return self.div_gallery.select_one('a div.caption').text

    def parseLink(self):
        a= self.div_gallery.select_one('a')
        return HOST + a['href']

    def parse_src(self):
        a = self.div_gallery.select_one('a')
        try:
            return a.select_one('img')['data-src']
        except KeyError:
            return 'https:' + a.select_one('img')['src']

    def parseId(self):
        a = self.div_gallery.select_one('a')
        return remove_prefix(a['href'], '/g/')[:-1]
