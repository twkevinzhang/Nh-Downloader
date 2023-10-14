## 功能
 - N站備份機: 
 輸入N站的搜尋結果網址，會自動備份其所有畫廊至`自訂的資料夾位置`
 - 單個本子備份:
 輸入本子的連結，備份整本本子至`自訂的資料夾位置`
 - 存檔模式:
可以將`DOWNLOAD_DIR_PATH`中的本子們存檔成zip，並且不壓縮畫質。請在`config.py`中設定`ZIP=True`及`ZIP_DIR_PATH`

## Todo
 - [ ] 製作 installer for windows
 
## 前置作業
- 自訂的資料夾位置
    - 在`config.py`的`DOWNLOAD_DIR_PATH`欄位輸入資料夾位置
    - (可選)在`config.py`的`ZIP_DIR_PATH`欄位輸入資料夾位置

## TL;DR
 - install python 3.8
 - run directly from source code:

        pip install -r requirements.txt
        git clone https://github.com/twkevinzhang/Nh-Downloader.git
        cd Nh-Downloader
        python main.py
