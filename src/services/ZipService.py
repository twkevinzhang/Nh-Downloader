import os
import shutil
from zipfile import ZipFile, BadZipFile
from src.entities.Book import Book
from const import logger, ZIP_DIR_PATH
from src.utilities.Utility import to_dir


class ZipService:
    def __init__(self, book: Book, unarchived_dir: str, zip_root: str = ZIP_DIR_PATH):
        self.book = book
        self.unarchived_dir = unarchived_dir
        self.zip_root = zip_root
        self.zip_name = to_dir(self.book.title) + ".zip"
        self.archived_path = os.path.join(self.zip_root, self.zip_name)
        self.log_prefix = f"[Page {0}]({self.book.max_page}){self.book.info_page_url[15:]}{self.book.title}"

    def zip(self):
        not_extension_archived_path = self.archived_path[:-4]
        shutil.make_archive(not_extension_archived_path, 'zip', self.unarchived_dir)
        logger.info(f"{self.log_prefix} zipped.")

    def hasZip(self) -> bool:
        if os.path.isfile(self.archived_path):
            try:
                archive_images = {file.filename for file in ZipFile(self.archived_path, 'r').infolist()}
                return self.book.image_names.issubset(archive_images)
            except BadZipFile as e:
                logger.error(f"Failed in check zip {self.archived_path}: ", e)
        return False
