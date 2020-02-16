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
    login_field = bank.find_login_element(driver)
    pin_field = bank.find_password_element(driver)
    login_button = bank.find_login_button_element(driver)

    # Click away the cookie button, maximum wait for 2 seconds
    t_max_cookie = 2
    t = 0
    while t <= t_max_cookie:
        try:
            cookie_button = bank.find_cookie_close_element(driver)
            cookie_button.click()
            break
        except:
            print('Wait for cookie banner {:.1f} sec'.format(t))
            t = t + 0.1
            sleep(0.1)
    if t > t_max_cookie:
        print('No cookie banner found, continue anyway')
        print('')

    # Login
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


def read_pages(bank, driver: webdriver, last_known_pdf: str) -> str:
    # returns latest pdf name

    # Reset counters
    new_head_pdf = ''
    cnt_pdf = 0
    cnt_html = 0
    page = 0

    while True:
        page = page + 1
        print('----------------------------------------------')
        print('Downloading page {:d}'.format(page))
        print()

        # Scroll down to show the page number
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        sleep(1)

        # Get links and extract direct PDF-URLs from the links
        pdf_links = bank.find_pdf_links(driver)
        pdf_urls = []
        for pdfLink in pdf_links:
            pdf_urls.append(pdfLink.get_attribute("href"))

        # Get the HTML links
        html_links = bank.find_pseudo_pdf_links(driver)
        html_urls = []
        for htmlLink in html_links:
            html_urls.append(htmlLink.get_attribute("href"))

        # Download all the PDFs to the default directory
        error = False

        for pdf_url in pdf_urls:

            try:
                # Get short URL -> use part after last '/', use part before '?'
                pdf_name = bank.extract_pdf_from_link(pdf_url)

                # Sometimes, Termingebundenes is .pdf despite being HTML -> check
                if bank.is_pseudo_pdf(pdf_name):
                    cnt_html = cnt_html + 1
                    print('Skip {:4d}: {:s}'.format(cnt_html, pdf_name))

                else:  # Skip possibly HTML
                    cnt_pdf = cnt_pdf + 1

                    # check if pdf is last-known-pdf, then done
                    if pdf_name == last_known_pdf:
                        print('------------------------------------')
                        print("found last known pdf: '{:s}'".format(last_known_pdf))
                        print('exiting...')

                        return new_head_pdf

                    # use it as new head pdf, if its first one
                    if cnt_pdf == 1:
                        new_head_pdf = pdf_name
                        print("updated new head to url: '{:s}'".format(pdf_name))

                    driver.get(pdf_url)
                    sleep(0.1)
                    print('Get  {:4d}: {:s}'.format(cnt_pdf, pdf_name))

            except:
                driver.back()
                print('Error, failed to load {:s}'.format(pdf_url))
                error = True
                break

        # Go to the next page
        if not error:

            # Show how many URLS were skipped
            for htmlUrl in html_urls:
                cnt_html = cnt_html + 1
                x = htmlUrl.split('/')
                html_url_short = x[-1]
                print('Skip {:4d}: {:s}'.format(cnt_html, html_url_short))
            print()

            # Check if there is another right button - stop if not
            try:
                right_button = bank.find_next_page_button()
            except:
                print('----------------------------------------------')
                print('Downloaded -> {:5d} documents'.format(cnt_pdf))
                print('Skipped    -> {:5d} documents'.format(cnt_html))
                print('No more right button -> End of download')
                print('----------------------------------------------')
                break
            driver.execute_script("arguments[0].click();", right_button)

        # Stop on error
        else:
            break
    return new_head_pdf


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
    new_head_pdf = read_pages(bank, driver, last_known_pdf)

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
        driver.get(bank.logout_url)
        sleep(1)
        drv.close()


# ------------------------------------------------------------------------------
# Login and download
drv = login_with_browser(comdirect)
scrap_pdfs(comdirect, drv)
logout_and_close(comdirect, drv)

# ------------------------------------------------------------------------------
