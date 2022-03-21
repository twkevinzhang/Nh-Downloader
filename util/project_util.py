import os
import re
import sys
import traceback
from zipfile import ZipFile

from bs4 import BeautifulSoup
import json
from const import logger
from const import *

# Project
from src.utilities.Utility import to_dir


def get_last_page(html):
    href = BeautifulSoup(html, 'html.parser').select_one('section.pagination a.last')['href']
    return int(re.search(r'\d*$', href).group(0))

def mkdir(*paths):
    for path in paths:
        try:
            os.makedirs(path)
            return path
        except FileExistsError:
            return path
        except OSError:
            pass

def zip_list_file_generator():
    print("生產目錄清單中...")
    f = open(ZIP_LIST_TEMP_NAME, 'w' if os.path.isfile(ZIP_LIST_TEMP_NAME) else 'a', encoding='utf-8')
    for zip in os.listdir(ZIP_DIR_PATH):
        f.write(getZipList(zip) + "\n")
    print("生產完畢")

def getZipList(zip:str) -> str:
    file_list = [file.filename for file in ZipFile(ZIP_DIR_PATH+"/"+to_dir(zip),'r').infolist() if isImg(file.filename)]
    return json.dumps({
        "title": zip,
        "file_list": file_list
    }, ensure_ascii=False)

def dir_list_file_generator():
    print("生產目錄清單中...")
    f = open(DIR_LIST_TEMP_NAME, 'w' if os.path.isfile(DIR_LIST_TEMP_NAME) else 'a', encoding='utf-8')
    for dir in os.listdir(DOWNLOAD_DIR_PATH):
        f.write(getDirList(dir) + "\n")
    print("生產完畢")

def getDirList(dir):
    file_list = [name for name in os.listdir(DOWNLOAD_DIR_PATH + "/" + to_dir(dir)) if isImg(name)]
    return json.dumps({
        "title": dir,
        "file_list": file_list
    }, ensure_ascii=False)

def isImg(name):
    return re.search(r'^\d+(\.jpg|png|gif)*$', name)

def make(s) -> str:
    return re.sub(r'([^\w\s]|\s)','',s).lower()
