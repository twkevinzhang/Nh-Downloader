import grequests
import requests
from bs4 import BeautifulSoup
from requests.structures import CaseInsensitiveDict

from src.entities.ResultItem import ResultItem
from src.parsers.BookParser import BookParser
from src.parsers.ResultPageParser import PAGE_PREFIX, ResultPageParser
from src.services.BookService import BookService
from src.services.ZipService import ZipService


class ResultService:
    def __init__(self, headers: CaseInsensitiveDict, url: str):
        self.headers = headers
        self.url = url
        self.items: set[ResultItem] = set()

    def scrapy_items(self, startPage: int, endPage: int):
        response_list = grequests.imap(
            (grequests.get(
                self.url + PAGE_PREFIX + str(page),
                headers=self.headers,
            ) for page in range(startPage, endPage)),
            size=10,
            # TODO: retry
            exception_handler=lambda request, exception: print(f"ResultPage{-1} failed: ", exception)
        )
        for response in response_list:
            parser = ResultPageParser(BeautifulSoup(response.content, 'html.parser'))
            self.items |= parser.parseItems()

    def get_items(self):
        return self.items