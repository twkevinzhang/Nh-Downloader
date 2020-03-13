# coding:utf-8
from datetime import datetime
import config

# info
DEVELOPMENT = True
__version__ = 0.1
PROJECT_NAME="Nh-Downloader"

# path
HOST = 'https://nhentai.net/'
GALLERY_PATH="https://i.nhentai.net"
DOWNLOAD_DIR_PATH=config.DOWNLOAD_DIR_PATH

# File Name
now=datetime.now().strftime('%Y%m%d_%H%M%S')
BOOK_INFO_FINE_NAME="book_info.txt"
METADATA_FILE_NAME="metadata.json"
LOG_FILE_NAME="./log/"+now+".log"
DIR_LIST_TEMP_NAME='dir_list_temp.txt'

# thread
THREAD_CNT=30
WAIT_OTHER_THREAD=True

# var
USE_JPN_TITLE=True
RETRY_CNT=10
RETRY_DELAY=10
CLOUD_MODE=config.CLOUD_MODE
