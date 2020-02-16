# Bank PDF Scraper in Python
* tested with MX-Linux 19 (Debian10-Derivat), python 3.7.3
* Ubuntu 18.04, python 3.6.9

## required packages
* python3-selenium
* chromedriver
* chromium

## init / design
- currently supports only comdirect, but extendable for other banks
- bank-specific config and logic via `/configs/bank.py`
    - see [configs/comdirect.py](configs/comdirect.py)
- bank-specific config imports user-specific configuration via `/configs/bank_config.py`
    - see sample config [configs/comdirect_config.py.sample](configs/comdirect_config.py.sample)
    ```
    login = '012345678'
    password = '123456'
    
    downloads = '/home/user/Downloads'
    file_head = '/home/user/comdirect_head.txt'
    archive = False
    close = False

    ```

## usage

- call it in terminal via
    ```
    # non-interactive without the -i
    python3 -i scraper.py
    ```
  
- opens browser, inserts login and password
- 2 Factor authentication is needed for comdirect - use photoTAN in browser
- different usage modes
- closes browser if bank-config states `close = True`

## usage modes

### default
- all PDFs in inbox will be downloaded, except links containing "Termingebundenes" which sometimes cause bugs due to html-links
- you can stop the script at any time via `ctrl + d`

### archive
- you can download the whole archive through the configuration
    ```
    archive = True
    ```
  
### delta
- usually you just want to download all new files, therefore the scraper needs to store the last downloaded file
- this is done through the configuration
    ```
    file_head = '/home/user/comdirect_head.txt'
    ```
- that file will contain the latest pdf-file-name of the last run and will be used as reference
    - all files will be downloaded until that file is reached
    - afterwards the file will be updated and the previous file is stored as backup (and will be overridden on next succesful run) 

### interactive
- not needed for delta mode
