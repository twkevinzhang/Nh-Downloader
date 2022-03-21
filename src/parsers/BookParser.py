from src.entities.Book import Book
from util.project_util import *
from util.util import *


class BookParser:
    def __init__(self, soup: BeautifulSoup, info_page_url: str):
        self.soup = soup
        self.info_page_url = info_page_url

    def parse(self) -> Book:
        book = Book()
        book.info_page_url = self.info_page_url
        book.gid = self.parseGid()
        book.title = self.parseTitle()
        book.max_page = self.parseMaxPage()
        book.image_names = self.parseImageNames()
        return book

    def parseGid(self) -> str:
        # TODO: img[src^="https://"][src$="/cover.jpg"],img[src^="https://"][src$="/cover.png"]
        return remove_suffix(
            remove_prefix(self.soup.select_one("meta[property='og:image']")['content'], ".*/galleries/"),
            "/cover.\w*"
        )

    def parseTitle(self) -> str:
        if USE_JPN_TITLE:
            try:
                return self.soup.select_one("div#info h2").text
            except AttributeError:
                pass
        return self.soup.select_one("div#info h1").text

    def parseMaxPage(self) -> int:
        return int(self.soup.select_one("div#info section#tags a[class='tag'] span.name").text)

    def parseImageNames(self) -> set[str]:
        # TODO: ['1.jpg', '2.png' ...]
        return {f"{i + 1}.{ele['src'][-3:]}" for i, ele in
                enumerate(self.soup.select('a.gallerythumb img[src^="https://"]'))}
