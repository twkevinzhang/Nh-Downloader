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
            def book_info_response_hook(response, *request_args, **request_kwargs):
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    book = BookParser(soup, factory_kwargs['bookUrl']).parse()
                    self.book_infos.add(book)
                else:
                    raise Exception(f'status code is {response.status_code}')
                return response
            return book_info_response_hook

        response_list = grequests.imap(
            (grequests.get(
                item.url,
                headers=self.headers,
                hooks={'response': [hook_factory(bookUrl=item.url)]},
            ) for item in self.items),
            # TODO: retry
            exception_handler=lambda request, exception: logger.error(f"BookInfo failed, url: {request.url} exception: {exception}")
        )
        [x for x in response_list]

    def get_book_infos(self) -> set[Book]:
        return self.book_infos