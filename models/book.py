import asyncio
import functools
import shutil
from zipfile import ZipFile, BadZipFile

from util.project_util import *
from util.session import Session
from util.util import *
from util.logger import logger


class Book:
    def __init__(self, info_page_url,log_option=dict):
        self.info_page_url = info_page_url
        res = Session().request("GET", self.info_page_url)
        if res is None: return
        self.soup = BeautifulSoup(res.content, 'html.parser')

        self.title = None
        self.log_option = log_option
        self.gid = None
        self.token = None
        self.tumb_url = None
        self.max_page = 0

        self.download_path=None

        self.init_from_net()

    def init_from_net(self):
        # gid, tumb_url
        self.tumb_url = self.soup.select_one("div#cover img")['data-src']
        self.gid = remove_suffix(remove_prefix(self.tumb_url,".*/galleries/"),"/cover.jpg")
        self.token = None
        self.archiver_key = None

        # title
        self.title = self.soup.select_one("div#info h1").text
        if USE_JPN_TITLE:
            try:
                self.title = self.soup.select_one("div#info h2").text
            except AttributeError: pass
        self.download_path=os.path.join(DOWNLOAD_DIR_PATH,check_dir_name(self.title))

        # max_page
        self.max_page =  int(self.soup.select_one("div#info section#tags a[class='tag'] span.name").text)

        # file_name
        self.file_name={f"{i+1}.{ele['src'][-3:]}" for i,ele in enumerate(self.soup.select('a.gallerythumb img[src^="https://"]'))}

    def download(self):
        if ZIP:
            if not (self.checkZipTemp() if ZIP_DIR_IN_CLOUD else self.checkZip()):
                self.download_book()
                shutil.make_archive(os.path.join(ZIP_DIR_PATH,check_dir_name(self.title)), 'zip',self.download_path)
            if ZIP_DIR_IN_CLOUD:
                open(ZIP_LIST_TEMP_NAME, 'a', encoding='utf-8').write(
                    getZipList(self.title) + "\n")
            logger.info("ZIP內容完整({}):[{}]{}".format(self.max_page, self.log_option['result_page'], self.title))
        else:
            self.download_book()

    def checkZip(self) ->bool:
        path=os.path.join(ZIP_DIR_PATH,check_dir_name(self.title))
        if os.path.isfile(path+".rar"): return True # fixme
        path+=".zip"
        if os.path.isfile(path):
            try:
                return make(check_dir_name(self.title)) in {make(x) for x in os.listdir(ZIP_DIR_PATH)} and \
                    self.file_name.issubset({file.filename for file in ZipFile(path,'r').infolist()})
            except BadZipFile as e:
                logger.error(f"{e}, {path}")
        return False

    def checkZipTemp(self) ->bool:
        if not os.path.isfile(ZIP_LIST_TEMP_NAME):
            raise BaseException('nesl error: zip_temp.txt not exist.')
        for l in open(ZIP_LIST_TEMP_NAME, 'r', encoding='utf-8'):
            l = json.loads(l)
            if l["title"] == check_dir_name(self.title) and self.file_name.issubset(set(l["file_list"])):
                logger.info("在清單之中， 頁數正確({}):[{}]{}".format(self.max_page, self.log_option['result_page'], self.title))
                return True
        return False

    def checkDir(self)->bool:
        if os.path.isdir(self.download_path):
            if self.file_name.issubset({x for x in os.listdir(self.download_path) if os.stat(os.path.join(self.download_path,x)).st_size>1000}):
                logger.info("頁數完整({}):[{}]{}".format(self.max_page, self.log_option['result_page'], self.title))
                return True
            logger.warning("發現舊資料不夠齊全，刪掉重載...") # fixme
            shutil.rmtree(self.download_path)
        return False

    def checkDirTemp(self)->bool:
        if not os.path.isfile(DIR_LIST_TEMP_NAME):
            raise BaseException('nesl error: DIR_LIST_TEMP.TXT not exist.')
        for l in open(DIR_LIST_TEMP_NAME, 'r', encoding='utf-8'):
            l = json.loads(l)
            if l["title"] == check_dir_name(self.title) and self.file_name.issubset(set(l["file_list"])):
                logger.info("在清單之中， 頁數正確({}):[{}]{}".format(self.max_page, self.log_option['result_page'], self.title))
                return True
        return False

    def downloaded_book(self, checkTemp=DOWNLOAD_DIR_IN_CLOUD):
        return self.checkDirTemp() if checkTemp else self.checkDir()

    def download_book(self):
        async def job():
            logger.info("[{}](pages:{}){}".format(self.log_option['result_page'], self.max_page, self.title))
            mkdir(self.download_path)
            def downloaded_img(img_title):
                if os.path.isfile(os.path.join(self.download_path,img_title)):
                    return True
                return False

            async def fetch(filename):
                url='{}/galleries/{}/{}'.format(GALLERY_PATH, self.gid, filename)
                url=url.replace('/cover.png','')
                if downloaded_img(filename): return

                res=None
                cnt=-1
                msg=f"got:{url}({self.max_page})"
                s=None
                while True:
                    res=await asyncio.get_event_loop().run_in_executor(None,functools.partial(
                        Session().request,
                        method="GET",
                        url=url,
                        title=self.title
                    ))

                    cnt+=1
                    s=msg+f",重試({cnt})"
                    if cnt!=0 and cnt % 10==0:
                        logger.warning(s)
                        break
                    if res != None and len(res.content)>1000:
                        break
                    else:
                        # logger.warn("loss:{},({})".format(url, self.max_page))
                        pass

                open(os.path.join(self.download_path,filename) , 'wb').write(res.content)
                logger.info(s if cnt!=0 else msg)

            await asyncio.gather(
                *[fetch(name) for name in self.file_name]
            )

            if not self.downloaded_book(checkTemp=False):
                book_logger(self.title, "圖片數量有缺")
            elif DOWNLOAD_DIR_IN_CLOUD:
                open(DIR_LIST_TEMP_NAME, 'a', encoding='utf-8').write(
                    getDirList(self.title) + "\n")

        if not self.downloaded_book():
            asyncio.run(job())
