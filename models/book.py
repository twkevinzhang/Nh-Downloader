import asyncio
import functools
import shutil
from zipfile import ZipFile, BadZipFile

from util.project_util import *
from util.session import Session
from util.util import *
from const import logger


class Book:
    def __init__(self, info_page_url,log_option=dict):
        self.info_page_url = info_page_url
        self.title = None
        self.log_option = log_option
        self.gid = None
        self.max_page = 0
        self.file_name=None
        self.download_path=None
        self.init_from_net()

    def init_from_net(self):
        soup=None
        res=None

        # gid
        cnt=0
        while True:
            try:
                res = Session().request("GET", self.info_page_url)
                soup = BeautifulSoup(res.content, 'html.parser')
                self.gid = remove_suffix(remove_prefix(soup.select_one("meta[property='og:image']")['content'],".*/galleries/"),"/cover.\w*")
                break
            except TypeError:
                cnt+=1
                logger.warning(f"沒有抓到gid，重試({cnt}): {self.info_page_url}")
                pass
        if res == None:
            return

        # title
        if USE_JPN_TITLE:
            try:
                self.title = soup.select_one("div#info h2").text
            except AttributeError:
                pass

        if self.title==None or len(self.title)==0:
            self.title = soup.select_one("div#info h1").text

        # download path
        self.download_path=os.path.join(DOWNLOAD_DIR_PATH,check_dir_name(self.title))

        # max_page
        self.max_page =  int(soup.select_one("div#info section#tags a[class='tag'] span.name").text)

        # file_name
        self.file_name={f"{i+1}.{ele['src'][-3:]}" for i,ele in enumerate(soup.select('a.gallerythumb img[src^="https://"]'))}

    def download(self):
        def func():
            async def job():
                logger.info(f"[{self.log_option['result_page']}](pages:{self.max_page}){self.title}")
                mkdir(self.download_path)
                def downloaded_img(img_title):
                    if os.path.isfile(os.path.join(self.download_path,img_title)):
                        return True
                    return False

                async def fetch(filename):
                    url=f'{GALLERY_PATH}/galleries/{self.gid}/{filename}'
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
                    if res is not None:
                        open(os.path.join(self.download_path,filename) , 'wb').write(res.content)
                    logger.debug(s if cnt!=0 else msg)

                await asyncio.gather(
                    *[fetch(name) for name in self.file_name]
                )

            if not self.downloaded_book(rm=True):
                asyncio.run(job())
            if not self.downloaded_book(checkTemp=False):
                logger.warning(f"圖片數量有缺: {self.title},gid:{self.gid}")
            else:
                if DOWNLOAD_DIR_IN_CLOUD:
                    open(DIR_LIST_TEMP_NAME, 'a', encoding='utf-8').write(
                        getDirList(self.title) + "\n")
                logger.info(f"downloaded({self.max_page}):[{self.log_option['result_page']}]{self.title}")

        if ZIP:
            if ZIP_DIR_IN_CLOUD and self.checkZipTemp():
                logger.info(f"在清單之中， 頁數正確({self.max_page}):[{self.log_option['result_page']}]{self.title}")
            elif not ZIP_DIR_IN_CLOUD and self.checkZip():
                logger.info(f"ZIP內容完整({self.max_page}):[{self.log_option['result_page']}]{self.title}")
            else:
                func()
                shutil.make_archive(os.path.join(ZIP_DIR_PATH,check_dir_name(self.title)), 'zip',self.download_path)
                logger.info(f"ZIPed({self.max_page}):[{self.log_option['result_page']}]{self.title}")

            if ZIP_DIR_IN_CLOUD:
                open(ZIP_LIST_TEMP_NAME, 'a', encoding='utf-8').write(
                    getZipList(self.title) + "\n")
        else:
            func()

    def checkZip(self) ->bool:
        path=os.path.join(ZIP_DIR_PATH,check_dir_name(self.title))
        if IGNORED_RAR and os.path.isfile(path+".rar"):
            return True # fixme
        path+=".zip"
        if os.path.isfile(path):
            try:
                return make(check_dir_name(self.title)) in {make(x)[:-3] for x in os.listdir(ZIP_DIR_PATH)} and \
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
                return True
        return False

    def checkDir(self)->bool:
        if os.path.isdir(self.download_path):
            if self.file_name.issubset({x for x in os.listdir(self.download_path) if os.stat(os.path.join(self.download_path,x)).st_size>1000}):
                return True
        return False

    def checkDirTemp(self)->bool:
        if not os.path.isfile(DIR_LIST_TEMP_NAME):
            raise BaseException('nesl error: DIR_LIST_TEMP.TXT not exist.')
        for l in open(DIR_LIST_TEMP_NAME, 'r', encoding='utf-8'):
            l = json.loads(l)
            if l["title"] == check_dir_name(self.title) and self.file_name.issubset(set(l["file_list"])):
                return True
        return False

    def downloaded_book(self, checkTemp=DOWNLOAD_DIR_IN_CLOUD,rm=False):
        b=None
        if checkTemp:
            b=self.checkDirTemp()
        else:
            b=self.checkDir()
            if not b:
                logger.warning(f"發現舊資料不夠齊全，刪掉重載... {self.title}")
                if rm and os.path.isdir(self.download_path):
                    shutil.rmtree(self.download_path, ignore_errors=True)
            else:
                logger.info(f"dir資料齊全 {self.title}")
        return b
