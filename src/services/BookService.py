import os
import grequests
from requests.structures import CaseInsensitiveDict
from src.entities.Book import Book
from const import logger, DOWNLOAD_DIR_PATH, GALLERIES_PATH
from src.utilities.Utility import to_dir


class BookService:
    def __init__(self, headers: CaseInsensitiveDict, book: Book, downloaded_dir: str = DOWNLOAD_DIR_PATH):
        self.headers = headers
        self.book = book
        self.downloaded_dir = downloaded_dir
        self.downloaded_path = os.path.join(self.downloaded_dir, to_dir(self.book.title))
        self.log_prefix = f"[Page 0]({self.book.max_page}){self.book.info_page_url[15:]}{self.book.title}"

    def get_downloaded_images(self) -> set[str]:
        return {f for f in os.listdir(self.downloaded_path) if os.path.isfile(os.path.join(self.downloaded_path, f))}

    def scrapy_images(self):
        logger.info(f"{self.log_prefix} Downloading... ")
        os.mkdir(self.downloaded_path)

        not_downloaded_images = self.book.image_names - self.get_downloaded_images()
        name_and_urls = {
            file_name: f'{GALLERIES_PATH}/{self.book.gid}/{file_name}' for file_name in not_downloaded_images
        }

        # download
        def hook_factory(*factory_args, **factory_kwargs):
            def image_response_hook(response, *request_args, **request_kwargs):
                open(os.path.join(self.downloaded_path, factory_kwargs['file_name']), 'wb').write(response.content)
                logger.debug(f"{factory_kwargs['url']} Downloaded.")
                return response
            return image_response_hook
        response_list = grequests.imap(
            (grequests.get(
                url,
                headers=self.headers,
                hooks={'response': [hook_factory(file_name=name, url=url)]},
            ) for name, url in name_and_urls.items()),
            size=10,
            # TODO: retry
            exception_handler=lambda request, exception: logger.error(f"Image failed, url: {request.url} exception: {exception}")
        )
        # 迭代 grequests.imap 時才會呼叫 grequests.get 去發送請求
        [x for x in response_list]

        # if has error
        failed_list = filter(lambda response: response.status_code != 200, response_list)
        if failed_list:
            logger.warning(
                f"{self.log_prefix} 圖片數量有缺")
        else:
            logger.info(
                f"{self.log_prefix} Downloaded.")