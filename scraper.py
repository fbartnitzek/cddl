import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# bank specific files
import configs.comdirect as comdirect

# ------------------------------------------------------------------------------
# Login and goto postbox
def login_with_browser(bank) -> webdriver:
    # Prepare and open the chrome driver
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {
        "download.default_directory": bank.config.downloads,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    }
                                           )
    driver = webdriver.Chrome('/usr/bin/chromedriver', options=chrome_options)

    driver.get(bank.login_url)

    # Get needed elements
    sleep(1)
    login_field = bank.find_login_element(driver)
    pin_field = bank.find_password_element(driver)
    login_button = bank.find_login_button_element(driver)

    # Click away the cook'header > div.loginlogout'ie button, maximum wait for 2 seconds
    bank.accept_cookie(driver)

    login_field.send_keys(bank.config.login)
    sleep(0.3)
    pin_field.send_keys(bank.config.password)
    sleep(0.3)
    login_button.click()
    sleep(1)

    # Wait until photoTAN is used and accepted
    cnt = 0
    while True:
        try:
            bank.find_2fa_ready_element1(driver)
            break
        except:
            cnt = cnt + 1
            print('Wait for postbox {:3d} sec'.format(cnt))
            sleep(1)

    # Goto postbox
    driver.get(bank.post_box_url)

    # Wait until photoTAN is used and accepted
    cnt = 0
    while True:
        try:
            bank.find_2fa_ready_element2(driver)
            break
        except:
            cnt = cnt + 1
            print('Wait for postbox {:3d} sec'.format(cnt))
            sleep(1)

    # optional use archive
    if bank.config.archive:
        bank.navigate_to_archive(driver)

    return driver


def scrap_pdfs(bank, driver: webdriver):

    # read last pdf-url from file
    current_head_file = bank.config.file_head
    try:
        # read id (first line) of doc
        with open(current_head_file, 'r') as f:
            last_known_id = f.readline().replace('\n', '').replace('\r', '')

    except FileNotFoundError:
        last_known_id = ''
    print("last known pdf: '{:s}'".format(last_known_id))

    # collect all files until last head file [id, name]
    new_head_doc = bank.read_pages(driver, last_known_id)

    # replace old head with new head?
    if new_head_doc is not None:

        # old to backup - should replace on unix
        os.rename(current_head_file, current_head_file + '.bak')
        print("new head doc: ")
        print(new_head_doc)

        # write new_head_pdf_url to file
        try:
            with open(current_head_file, 'w+') as f:
                f.write('\n'.join(new_head_doc))
            print("updated new head file to: {:s} - {:s}".format(new_head_doc[0], new_head_doc[1]))
        except FileNotFoundError:
            print('should never happen')


def logout_and_close(bank, driver: webdriver):
    if bank.config.close:
        bank.logout(driver)
        sleep(1)
        drv.close()


# ------------------------------------------------------------------------------
# Login and download comdirect
drv = login_with_browser(comdirect)
scrap_pdfs(comdirect, drv)
logout_and_close(comdirect, drv)
