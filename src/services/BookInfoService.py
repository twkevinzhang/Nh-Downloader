import os
import grequests
from bs4 import BeautifulSoup
from requests.structures import CaseInsensitiveDict
from src.entities.Book import Book
from const import logger, DOWNLOAD_DIR_PATH, GALLERIES_PATH
from src.entities.ResultItem import ResultItem
from src.parsers.BookParser import BookParser
from src.utilities.Utility import to_dir


class BookInfoService:
    def __init__(self, headers: CaseInsensitiveDict, items: list[ResultItem]):
        self.headers = headers
        self.items = items
        self.book_infos: set[Book] = set()

    def scrapy_book_infos(self):
        def hook_factory(*factory_args, **factory_kwargs):
            def book_info_response_hook(res, *request_args, **request_kwargs):
                soup = BeautifulSoup(res.content, 'html.parser')
                book = BookParser(soup, factory_kwargs['bookUrl']).parse()
                self.book_infos.add(book)
                return res
            return book_info_response_hook

        response_list = grequests.imap(
            (grequests.get(
                item.url,
                headers=self.headers,
                hooks={'response': [hook_factory(bookUrl=item.url)]},
            ) for item in self.items),
            size=10,
            # TODO: retry
            exception_handler=lambda request, exception: logger.error(f"BookInfo failed, url: {request.url} exception: {exception}")
        )
        [x for x in response_list]

    def get_book_infos(self) -> set[Book]:
        return self.book_infos