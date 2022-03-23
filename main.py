import sys
from bs4 import BeautifulSoup
from src.parsers.BookParser import BookParser
from src.services.BookService import BookService
from src.entities.Book import Book
from models.result import Result
from src.headers.HeadersBuilder import HeadersBuilder
from src.services.ZipService import ZipService
from util.project_util import dir_list_file_generator, zip_list_file_generator
import grequests
import requests

if len(sys.argv) > 1:
    Result('https://nhentai.net/language/chinese/', start=int(sys.argv[1]), end=int(sys.argv[2]))

else:
    d = {
        'a': "下載搜尋結果",
        'b': "下載本子",
        'c': "生產目錄清單",
        'd': "生產ZIP清單",
        'input': ''
    }
    inp = input("\n".join([key + "> " + d[key] for key in d]))

    headers = HeadersBuilder().build()

    if inp == 'a':
        inp = input("輸入搜尋結果的連結: ")
        if inp == "#":
            Result('https://nhentai.net/language/chinese/', start=1)
        else:
            Result(inp.strip())

    elif inp == 'b':
        inp = input("輸入本子的連結: ")
        if inp == "#":
            url = 'https://nhentai.net/g/299246/'
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.content, 'html.parser')
            book= BookParser(soup, url).parse()
            service = BookService(headers, book)
            service.scrapy_images()
            zipService = ZipService(book, service.downloaded_path)
            zipService.zip()
            print('hasZip?', zipService.hasZip())
