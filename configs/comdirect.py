# noinspection PyUnresolvedReferences
import configs.comdirect_config as config
from selenium import webdriver
from time import sleep
import re
import doctest

# urls
login_url = 'https://kunde.comdirect.de/lp/wt/login?execution=e1s1&afterTimeout=true'
post_box_url = 'https://kunde.comdirect.de/itx/posteingangsuche'
post_box_url = 'https://kunde.comdirect.de/itx/posteingangsuche?execution=e3s3'
logout_url = 'https://kunde.comdirect.de/lp/wt/logout'


def find_login_element(driver: webdriver):
    return driver.find_element_by_name('param1')


def find_password_element(driver: webdriver):
    return driver.find_element_by_name('param3')


def find_login_button_element(driver: webdriver):
    return driver.find_element_by_id('loginAction')


def accept_cookie(driver: webdriver):
    t_max_cookie = 2
    t = 0
    while t <= t_max_cookie:
        try:
            # cookie_button = driver.find_element_by_id('closeCookieBanner')
            # cookie_button = driver.find_element_by_id('uc-btn-accept-banner')
            cookie_button = driver.find_element_by_id(
                'privacy-init-wall-button-accept')
            cookie_button.click()
            break
        except:
            print('Wait for cookie banner {:.1f} sec'.format(t))
            t = t + 0.1
            sleep(0.1)
    if t > t_max_cookie:
        print('No cookie banner found, continue anyway')
        print('')


def find_2fa_ready_element1(driver: webdriver):
    return driver.find_element_by_link_text("Alle Umsätze")


def find_2fa_ready_element2(driver: webdriver):
    return driver.find_element_by_link_text('Archiv')


def read_pages(driver: webdriver, last_known_id: str) -> str:
    # returns latest pdf name

    # Reset counters
    new_head_doc = None
    cnt_entry = 0
    cnt_fail = 0
    page = 0

    while True:
        page = page + 1
        print('----------------------------------------------')
        print('Downloading page {:d}'.format(page))
        print()

        # Scroll down to show the page number
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        sleep(1)

        # Get all doc-urls: href=/itx/nachrichten/dokumentenabruf/id/B708AB6FA385B5C3A87ACA8DDDC7C6F0
        entry_links = driver.find_elements_by_css_selector(
            "a[id*='urlAbfrage'][href^='/itx/nachrichten/dokumentenabruf/id/']")
        entry_urls = []
        for entry_link in entry_links:
            entry_urls.append(
                [entry_link.get_attribute("href"),
                 entry_link.get_attribute("text")])

        for entry in entry_urls:
            try:
                cnt_entry = cnt_entry + 1
                url = entry[0]
                text = entry[1]
                id = extract_id_from_url(url)

                if id == last_known_id:
                    print('------------------------------------')
                    print("found last known id: '{:s}'".format(last_known_id))
                    print('exiting...')
                    return new_head_doc
                
                print("download {:s} {:s} - {:s}".format(id, text, url))
                driver.get(url)
                sleep(0.1)

                if cnt_entry == 1:
                    new_head_doc = [id, text]
                    print("updated new head to id: '{:s}'".format(id))

            except:
                print('Error, failed to load {:s}'.format(id))
                driver.back()
                cnt_fail = cnt_fail + 1

        # Go to the next page
        try:
            # Check if there is another right button - stop if not
            right_button = find_next_page_button(driver)
        except:
            print('----------------------------------------------')
            print('Downloaded -> {:5d} documents'.format(cnt_entry))
            print('failed     -> {:5d} documents'.format(cnt_fail))
            print('No more right button -> End of download')
            print('----------------------------------------------')
            break
        driver.execute_script("arguments[0].click();", right_button)
    return new_head_doc


def extract_pdf_from_link(pdf_url: str):
    return (pdf_url.split('/')[-1]).split('?')[0]

def extract_id_from_url(url: str):
    """Return the doc-id of an url.

    >>> extract_id_from_url('https://kunde.comdirect.de/itx/nachrichten/dokumentenabruf/id/032567D703D3794FE916E466077AB304/predocument?selectEntryId=0')
    '032567D703D3794FE916E466077AB304'
    >>> extract_id_from_url('https://kunde.comdirect.de/itx/nachrichten/dokumentenabruf/id/7B5D56394C2F65FFED9D1F67A1F67F7C?selectEntryId=1')
    '7B5D56394C2F65FFED9D1F67A1F67F7C'
    >>> extract_id_from_url('/itx/nachrichten/dokumentenabruf/id/B708AB6FA385B5C3A87ACA8DDDC7C6F0')
    'B708AB6FA385B5C3A87ACA8DDDC7C6F0'
    """
    result = re.search(r"/id/([0-9A-Z]+)([/?].+)?$", url)
    if result:
        return result.group(1)
    else:
        return ""


def find_next_page_button(driver: webdriver):
    return driver.find_element_by_css_selector("a[id^='f1-j_idt'][id$='_right']")


def navigate_to_archive(driver: webdriver):
    find_2fa_ready_element(driver).click()

    # Select GESAMTER_ZEITRAUM
    zeitraum_select = driver.find_element_by_id('f1-zeitraumInput_pbInput')
    select_field = webdriver.support.ui.Select(zeitraum_select)
    select_field.select_by_value('GESAMTER_ZEITRAUM')

    # Start search
    suchen_field = driver.find_element_by_link_text('Suchen')
    suchen_field.click()


def logout(driver: webdriver):
    driver.get(logout_url)

if __name__ == "__main__":
    import doctest
    doctest.testmod()