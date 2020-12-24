# coding:utf-8
import sys
from datetime import datetime
import config
from loguru import logger

# info
DEVELOPMENT = True
__version__ = 0.1
PROJECT_NAME="Nh-Downloader"

# path
HOST = 'https://nhentai.net/'
GALLERY_PATH="https://i.nhentai.net"
DOWNLOAD_DIR_PATH=config.DOWNLOAD_DIR_PATH
ZIP_DIR_PATH=config.ZIP_DIR_PATH
ZIP=config.ZIP

# File Name
now=datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE_NAME="./log/"+now+".log"
DIR_LIST_TEMP_NAME='dir_list_temp.txt'
ZIP_LIST_TEMP_NAME='zip_list_temp.txt'

# var
USE_JPN_TITLE=True
RETRY_CNT=10
DOWNLOAD_DIR_IN_CLOUD=config.DOWNLOAD_DIR_IN_CLOUD
ZIP_DIR_IN_CLOUD=config.ZIP_DIR_IN_CLOUD

# log
format="{time:YYYY-MM-DD HH:mm:ss} [{thread.name}]<lvl>[{level}] {function}(): {message}</>"
config = {
    "handlers": [
        {"sink": sys.stdout, "format": format},
        {"sink":LOG_FILE_NAME, "format": format,'encoding':'utf-8'},
    ]
}
# logger.add(LOG_FILE_NAME,format=format,encoding='utf-8')
logger.configure(**config)
