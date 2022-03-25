import os
from const import logger, DOWNLOAD_DIR_PATH, GALLERIES_PATH
import grequests
from bs4 import BeautifulSoup
from src.parsers.BookParser import BookParser
from src.parsers.ResultPageParser import ResultPageParser, PAGE_PREFIX
from src.services.BookInfoService import BookInfoService
from src.headers.HeadersBuilder import HeadersBuilder
from src.services.ImageService import ImageService
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

    # download ResultPages
    startPage = 1
    endPage = 3
    urls = {result_url + PAGE_PREFIX + str(page) for page in range(startPage, endPage)}
    resultService = ResultService(headers, urls)
    resultService.scrapy_items()
    # storageService.save_items(resultService.get_items())
    items = resultService.get_items()

    # download BookInfos
    bookInfoService = BookInfoService(headers, items)
    bookInfoService.scrapy_book_infos()
    # storageService.save_book_infos(bookInfoService.get_book_infos())
    books = bookInfoService.get_book_infos()

    for book in books:
        # download Images
        imageService = ImageService(headers, book)
        imageService.scrapy_images()

        # zipping
        # TODO: multithreading
        zipService = ZipService(book, imageService.downloaded_path)
        zipService.zip()

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
    service = ImageService(headers, book)
    service.scrapy_images()
    zipService = ZipService(book, service.downloaded_path)
    zipService.zip()
