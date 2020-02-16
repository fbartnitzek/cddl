# noinspection PyUnresolvedReferences
import configs.comdirect_config as config
from selenium import webdriver

# urls
login_url = 'https://kunde.comdirect.de/lp/wt/login?execution=e1s1&afterTimeout=true'
post_box_url = 'https://kunde.comdirect.de/itx/posteingangsuche'
logout_url = 'https://kunde.comdirect.de/lp/wt/logout'


def find_login_element(driver: webdriver):
    return driver.find_element_by_name('param1')


def find_password_element(driver: webdriver):
    return driver.find_element_by_name('param3')


def find_login_button_element(driver: webdriver):
    return driver.find_element_by_id('loginAction')


def find_cookie_close_element(driver: webdriver):
    return driver.find_element_by_id('closeCookieBanner')


def find_2fa_ready_element(driver: webdriver):
    return driver.find_element_by_link_text('Archiv')


def find_pdf_links(driver: webdriver):
    return driver.find_elements_by_css_selector("a[id*='urlAbfrage'][href*='.pdf']")


def find_pseudo_pdf_links(driver: webdriver):
    return driver.find_elements_by_css_selector("a[id*='urlAbfrage'][href*='.html']")


def extract_pdf_from_link(pdf_url: str):
    return (pdf_url.split('/')[-1]).split('?')[0]


def is_pseudo_pdf(pdf_name: str):
    return 'Termingebundenes' in pdf_name


def find_next_page_button(driver: webdriver):
    return driver.find_element_by_css_selector("a[id='f1-j_idt123_right']")


def navigate_to_archive(driver: webdriver):
    find_2fa_ready_element(driver).click()

    # Select GESAMTER_ZEITRAUM
    zeitraum_select = driver.find_element_by_id('f1-zeitraumInput_pbInput')
    select_field = webdriver.support.ui.Select(zeitraum_select)
    select_field.select_by_value('GESAMTER_ZEITRAUM')

    # Start search
    suchen_field = driver.find_element_by_link_text('Suchen')
    suchen_field.click()
