import os
from const import logger, DOWNLOAD_DIR_PATH, GALLERIES_PATH
import grequests
from bs4 import BeautifulSoup
from src.parsers.BookParser import BookParser
from src.parsers.ResultPageParser import ResultPageParser, PAGE_PREFIX
from src.services.BookService import BookService
from src.headers.HeadersBuilder import HeadersBuilder
from src.services.ResultService import ResultService
from src.services.ZipService import ZipService
import requests

headers = HeadersBuilder().build()

d = {
    'a': "下載搜尋結果",
    'b': "下載本子",
    'c': "生產目錄清單",
    'd': "生產ZIP清單",
    'input': ''
}
inp = input("\n".join([key + "> " + d[key] for key in d]))

if inp == 'a':
    inp = input("輸入搜尋結果的連結: ")
    if inp == "#":
        result_url = 'https://nhentai.net/language/chinese'
    else:
        result_url = inp.strip()

    res = requests.get(result_url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    parser = ResultPageParser(soup)
    maxPage = parser.parseMaxPage()
    service = ResultService(headers, result_url)
    service.scrapy_items(1, 3)
    items = service.get_items()


    # download
    def hook_factory(*factory_args, **factory_kwargs):
        def response_hook(res, *request_args, **request_kwargs):
            soup = BeautifulSoup(res.content, 'html.parser')
            book = BookParser(soup, factory_kwargs['bookUrl']).parse()
            service = BookService(headers, book)
            service.scrapy_images()
            # TODO: multithreading
            zipService = ZipService(book, service.downloaded_path)
            zipService.zip()
            return res
        return response_hook
    response_list = grequests.imap(
        (grequests.get(
            item.url,
            headers=headers,
            hooks={'response': [hook_factory(bookUrl=item.url)]},
        ) for item in items),
        size=10,
        # TODO: retry
        exception_handler=lambda request, exception: logger.error(f"BookInfo failed, request: ", request, "exception: ", exception)
    )
    [x for x in response_list]

elif inp == 'b':
    inp = input("輸入本子的連結: ")
    url = None
    if inp == "#":
        url = 'https://nhentai.net/g/299246'
    else:
        url = inp.strip()

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    book = BookParser(soup, url).parse()
    service = BookService(headers, book)
    service.scrapy_images()
    zipService = ZipService(book, service.downloaded_path)
    zipService.zip()
