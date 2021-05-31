# noinspection PyUnresolvedReferences
import configs.comdirect_config as config
from selenium import webdriver
from time import sleep

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


def accept_cookie(driver: webdriver):
    t_max_cookie = 2
    t = 0
    while t <= t_max_cookie:
        try:
            # cookie_button = driver.find_element_by_id('closeCookieBanner')
            # cookie_button = driver.find_element_by_id('uc-btn-accept-banner')
            cookie_button = driver.find_element_by_id('privacy-init-wall-button-accept')
            cookie_button.click()
            break
        except:
            print('Wait for cookie banner {:.1f} sec'.format(t))
            t = t + 0.1
            sleep(0.1)
    if t > t_max_cookie:
        print('No cookie banner found, continue anyway')
        print('')


def find_2fa_ready_element(driver: webdriver):
    return driver.find_element_by_link_text('Archiv')


def read_pages(driver: webdriver, last_known_pdf: str) -> str:
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
        pdf_links = driver.find_elements_by_css_selector("a[id*='urlAbfrage'][href*='.pdf']")
        pdf_urls = []
        for pdfLink in pdf_links:
            pdf_urls.append(pdfLink.get_attribute("href"))

        # Get the HTML links
        html_links = driver.find_elements_by_css_selector("a[id*='urlAbfrage'][href*='.html']")
        html_urls = []
        for htmlLink in html_links:
            html_urls.append(htmlLink.get_attribute("href"))

        # Download all the PDFs to the default directory
        error = False

        for pdf_url in pdf_urls:

            try:
                # Get short URL -> use part after last '/', use part before '?'
                pdf_name = extract_pdf_from_link(pdf_url)

                # Sometimes, Termingebundenes is .pdf despite being HTML -> check
                if 'Termingebundenes' in pdf_name:
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
                right_button = find_next_page_button(driver)
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


def extract_pdf_from_link(pdf_url: str):
    return (pdf_url.split('/')[-1]).split('?')[0]


def find_next_page_button(driver: webdriver):
    return driver.find_element_by_css_selector("a[id='f1-j_idt125_right']")


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
