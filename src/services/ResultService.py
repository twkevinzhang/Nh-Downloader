import grequests
from bs4 import BeautifulSoup
from requests.structures import CaseInsensitiveDict
from src.entities.ResultItem import ResultItem
from src.parsers.ResultPageParser import ResultPageParser
from const import logger, DOWNLOAD_DIR_PATH, GALLERIES_PATH


class ResultService:
    def __init__(self, headers: CaseInsensitiveDict, urls: set[str]):
        self.headers = headers
        self.urls = urls
        self.items: set[ResultItem] = set()

    def scrapy_items(self):
        response_list = grequests.imap(
            (grequests.get(
                url,
                headers=self.headers,
            ) for url in self.urls),
            size=10,
            # TODO: retry
            exception_handler=lambda request, exception: logger.error(f"ResultPage failed, url: {request.url} exception: {exception}")
        )
        for response in response_list:
            parser = ResultPageParser(BeautifulSoup(response.content, 'html.parser'))
            self.items |= parser.parseItems()

    def get_items(self):
        return self.items