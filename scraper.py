import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# bank specific files
import configs.comdirect as comdirect
# import configs.frankfurtersparkasse as sparkasse


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

    # Login
    # sparkasse: element not interactable
    #   not helpful: driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

    login_field.send_keys(bank.config.login)
    sleep(0.3)
    pin_field.send_keys(bank.config.password)
    sleep(0.3)
    login_button.click()
    sleep(1)

    # Goto postbox
    driver.get(bank.post_box_url)

    # Wait until photoTAN is used and accepted
    cnt = 0
    while True:
        try:
            bank.find_2fa_ready_element(driver)
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
        with open(current_head_file, 'r') as f:
            last_known_pdf = f.read().replace('\n', '').replace('\r', '')
    except FileNotFoundError:
        last_known_pdf = ''
    print("last known pdf: '{:s}'".format(last_known_pdf))

    # collect all files until last head file
    # new_head_pdf = read_pages(bank, driver, last_known_pdf)
    new_head_pdf = bank.read_pages(driver, last_known_pdf)

    # replace old head with new head?
    if new_head_pdf != '' and new_head_pdf != last_known_pdf:

        # old to backup - should replace on unix
        os.rename(current_head_file, current_head_file + '.bak')

        # write new_head_pdf_url to file
        try:
            with open(current_head_file, 'w+') as f:
                f.write(new_head_pdf)
                print("updated new head file to url: '{:s}'".format(new_head_pdf))
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

# Login and download sparkasse
# drv = login_with_browser(sparkasse)
# scrap_pdfs(sparkasse, drv)
# logout_and_close(sparkasse, drv)

# ------------------------------------------------------------------------------
