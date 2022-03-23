from bs4 import BeautifulSoup
from src.entities.ResultItem import ResultItem
from src.parsers.ResultBookParser import ResultBookParser

PAGE_PREFIX = '/?page='


class ResultPageParser:
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def parseItems(self) -> set[ResultItem]:
        items = set()
        for div_gallery in self.soup.select('div.gallery'):
            item = ResultBookParser(div_gallery).parse()
            items.add(item)
        return items

    def parseMaxPage(self) -> int:
        href = self.soup.select_one(f"section.pagination a.last")['href']
        pageStringIndex = href.index(PAGE_PREFIX) + len(PAGE_PREFIX)
        page = int(href[pageStringIndex:])
        return page

