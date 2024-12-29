# noinspection PyUnresolvedReferences
import configs.comdirect_config as config
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import re
import doctest

# urls
login_url = 'https://kunde.comdirect.de/lp/wt/login?execution=e1s1&afterTimeout=true'
post_box_url = 'https://kunde.comdirect.de/itx/posteingangsuche'
logout_url = 'https://kunde.comdirect.de/lp/wt/logout'


def find_login_element(driver: webdriver):
    return driver.find_element_by_name('param1')


def find_password_element(driver: webdriver):
    return driver.find_element(By.XPATH, "//input[@name='param3']")

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


def find_new_docs(driver: webdriver, last_known_id: str) -> list:
    page = 0
    new_docs = []
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

        for entry_link in entry_links:
            url = entry_link.get_attribute("href")
            id = extract_id_from_url(url)
            if id == last_known_id:
                print('found last known doc: {:s}'.format(id))
                return new_docs
            
            new_docs.append([url, entry_link.get_attribute("text"), id])

        # Go to the next page
        try:
            # Check if there is another right button - stop if not
            right_button = find_next_page_button(driver)
        except:
            print('----------------------------------------------')
            print('New Docs -> {:5d} documents'.format(len(new_docs)))
            print('No more right button -> End of download')
            print('----------------------------------------------')
            break
        driver.execute_script("arguments[0].click();", right_button)
    return new_docs


def read_pages(driver: webdriver, last_known_id: str) -> list:
    # returns latest doc entry

    new_head_doc = None
    failed = 0
    downloaded = 0

    new_docs = find_new_docs(driver, last_known_id)

    if len(new_docs) > 0:
        for i in range(len(new_docs)):
            doc = new_docs[i]
            url = doc[0]
            text = doc[1]
            id = doc[2]
            print("download {:s} {:s} - {:s}".format(id, text, url))
            try:
                driver.get(url)
                sleep(0.1)
                downloaded = downloaded + 1
            except:
                print(
                    'Error, failed to load {:s} {:s} - {:s}'.format(id, text, url))
                driver.back()
                failed = failed + 1

            if i == 0:
                new_head_doc = [id, text]
                print("updated new head to id: '{:s}'".format(id))

        print('----------------------------------------------')
        print('found:       {:5d} documents'.format(len(new_docs)))
        print('downloaded:  {:5d} documents'.format(downloaded))
        print('failed:      {:5d} documents'.format(failed))
        print('----------------------------------------------')
        return new_head_doc

    print('No new docs found')
    return None


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
