import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from bs4 import BeautifulSoup as bs
from urllib.parse import quote, quote_plus, urlencode
import datetime
from dateutil.relativedelta import relativedelta
import time
import concurrent.futures
import chromedriver_binary  # Adds chromedriver binary to path
import cloudscraper # https://pypi.org/project/cloudscraper/

'''
    https://zeroscans.com/home
DONE    https://manga4life.com/
DONE    https://leviatanscans.com/
    https://lhtranslation.net/
    https://mangasushi.net/
    https://manhuaplus.com/
DOWN    https://mangadex.org/
DONE    https://manganelo.com/
DONE    https://reaperscans.com/home
'''
#
# For formatting the html: https://www.freeformatter.com/html-formatter.html#ad-output
# Set to true to save the html of the requested page
SAVE_OUTPUT = False
MAX_THREADS = 30

def check_websites():
    driver = setup_driver()
    urls = [['https://zeroscans.com/home', 'zeroscans'], ['https://leviatanscans.com/', 'leviatan'], ['https://lhtranslation.net', 'lhtranslation'],
            ['https://mangasushi.net/', 'mangasushi'], ['https://manhuaplus.com/', 'manhuaplus'], ['https://mangadex.org/', 'mangadex'],
            ['https://manganelo.com/', 'manganelo'], ['https://reaperscans.com/home', 'reaperscans'], ['https://manga4life.com/', 'mangalife']]
    for url in urls:
        driver.get(url[0])
        if SAVE_OUTPUT:
            save_page(driver, f'outputs/{url[1]}.html')

def setup_driver():
    # Add additional Options to the webdriver
    chrome_options = Options()
    # add the argument and make the browser Headless.
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("window-size=1024,768")
    chrome_options.add_argument("--no-sandbox")
    # Instantiate the Webdriver: Mention the executable path of the webdriver you have downloaded
    # For linux/Mac
    # driver = webdriver.Chrome(options = chrome_options)
    # For windows
    #executable_path=r"D:\Programming\angular\MangaSiteProject\MangaSiteAPI\app\chromedriver.exe", 
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def save_page(page, name='outputs/output.html'):    
    with open(name, 'w',  encoding="utf-8") as file:
        file.write(page.page_source)

############## General ##############
def update_manga(manga):
    latest_chapter = {'chapter_number': 0, 'date': 'Failed to get data', 'link': manga['link']}

    if manga['source'] == 'manga4life.com':
        latest_chapter = latest_chapter_mangalife(manga['link'])
    elif manga['source'] == 'manganelo.com':
        latest_chapter = latest_chapter_manganelo(manga['link'])
    elif manga['source'] == 'leviatanscans.com':
        latest_chapter = latest_chapter_leviatanscans(manga['link'])
    elif manga['source'] == 'reaperscans.com':
        latest_chapter = latest_chapter_reaperscans(manga['link'])
        
    manga['release_date'] = latest_chapter['date']
    manga['chapter_link'] = latest_chapter['link']
    manga['latest_chapter'] = latest_chapter['chapter_number']

    # Add small delay to avoid spamming the website too hard
    # TODO: Might be best to mix the websites as much as possible to reduce load on sites
    time.sleep(0.25)

def latest_chapters(mangas):
    threads = min(MAX_THREADS, len(mangas))

    if threads is not 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as exec:
            exec.map(update_manga, mangas)

    return mangas

def get_chapter_number(chapter_name):
    prev = '0'
    number = []
    decimal_found = False
    for i in chapter_name:
        # There should only be numbers after finding the decimal
        if decimal_found is True and not i.isdigit():
            break
        if i.isdigit() or (prev.isdigit() and i is '.'):
            number.append(i)
        if decimal_found is False and (prev.isdigit() and i is '.'):
            decimal_found = True
        prev = i
    return float(''.join(number))

############## https://manga4life.com/ ##############
def search_mangalife(name=''):
    base_url = 'https://manga4life.com'
    url = f'{base_url}/search/?'
    params = {'name': name}
    url += urlencode(params, quote_via=quote)

    driver = setup_driver()
    driver.get(url)
    
    try:
        className = 'SeriesName'
        # Need to wait for the browser to setup otherwise sometimes it is too fast
        # and results in a "Stale element reference: element is not attached to the page of the document"
        time.sleep(1)
        element = WebDriverWait(driver, 5).until(lambda s: s.find_element_by_class_name(className).is_displayed())
        if SAVE_OUTPUT:
            save_page(driver)
        soup = bs(driver.page_source, 'html.parser')

        results = soup.find_all(class_=className)
        if len(results) <= 0:
            print('nothing')
            return []

        mangas = []
        i = 0
        while i < len(results) - 1:
            elem1 = results[i]
            elem2 = results[i + 1]

            img_elem = elem1.find('img')
            if img_elem is not None:
                link = base_url + elem1['href']
                manga_name = elem2.text.strip()
                img_src = img_elem['src']
                mangas.append({'link': link, 'img_src': img_src, 'name': manga_name})
            else:
                img_elem = elem2.find('img')
                link = base_url + elem2['href']
                manga_name = elem1.text.strip()
                img_src = img_elem['src']
                mangas.append({'link': link, 'img_src': img_src, 'name': manga_name})
            i += 2
    finally:
        driver.quit()
    
    return mangas
   
def latest_chapter_mangalife(url):
    driver = setup_driver()
    driver.get(url)

    try:
        className = 'ChapterLink'
        # Need to wait for the browser to setup otherwise sometimes it is too fast
        # and results in a "Stale element reference: element is not attached to the page of the document"
        time.sleep(2)
        element = WebDriverWait(driver, 5).until(lambda s: s.find_element_by_class_name(className).is_displayed())
        if SAVE_OUTPUT:
            save_page(driver)

        soup = bs(driver.page_source, 'html.parser')

        results = soup.find_all(class_=className)
        if len(results) <= 0:
            return []
        
        latest_chapter = {'chapter_number': 0, 'date': datetime.datetime.min, 'link': ''}
        for elem in results:
            link = 'https://manga4life.com' + elem['href']
            span_elems = elem.find_all('span')
            chapter_number = 0
            date = datetime.datetime.min
            for span in span_elems:
                if span.has_attr('class') and 'float-right' in span['class']:
                    try:
                        date = datetime.datetime.strptime(span.text.strip(), '%m/%d/%Y')
                    except ValueError:
                        date_text = span.text.strip().lower()
                        if 'yesterday' in date_text:
                            date = datetime.datetime.now() - datetime.timedelta(1)
                        elif 'hour' in date_text:
                            date = datetime.datetime.now()
                        else:
                            print('Error: Unknown date format given.')
                elif span.has_attr('class') and not ('badge' in span['class']) and not ('LastRead' in span['class']): 
                    chapter_number = get_chapter_number(span.text.strip())

            if date > latest_chapter['date'] or (date == latest_chapter['date'] and chapter_number > latest_chapter['chapter_number']):
                latest_chapter['date'] = date
                latest_chapter['chapter_number'] = chapter_number
                latest_chapter['link'] = link

        latest_chapter['date'] = latest_chapter['date'].strftime('%m/%d/%Y')

    finally:
        driver.quit()

    return latest_chapter

############## https://manganelo.com ##############
def clean_name(name):
    words = name.split(' ')
    # remove empty spaces
    words = [w for w in words if w]
    # combine words with underscores
    return '_'.join(words)


def search_manganelo(name=''):
    base_url = 'https://manganelo.com'
    name = clean_name(name)
    url = f'{base_url}/search/story/{quote(name)}'

    page = requests.get(url)
    soup = bs(page.content, 'html.parser')
    className = 'search-story-item'
    results = soup.find_all(class_=className)
    if len(results) <= 0:
        print('nothing')
        return []
    mangas = []
    for elem in results:
        link_elem = elem.find('a', 'item-img')
        img_elem = link_elem.find('img')

        link = link_elem['href']
        manga_name = link_elem['title']
        img_src = img_elem['src']

        mangas.append({'link': link, 'img_src': img_src, 'name': manga_name})
    return mangas

def latest_chapter_manganelo(url):
    page = requests.get(url)
    soup = bs(page.content, 'html.parser')
    className = 'row-content-chapter'
    results_container = soup.find(class_=className)
    results = results_container.find_all(class_='a-h')
    if len(results) <= 0:
        return []
    latest_chapter = {'chapter_number': 0, 'date': datetime.datetime.min, 'link': ''}
    for elem in results:
        link_elem = elem.find('a', class_='chapter-name')
        date_elem = elem.find('span', class_='chapter-time')

        if None in (link_elem, date_elem):
            continue

        link = link_elem['href']
        chapter_number = get_chapter_number(link_elem.text.strip())
        # Example format: Mar 27,2021 08:03
        # Code documentation: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        date = datetime.datetime.strptime(date_elem['title'], '%b %d,%Y %H:%M')

        if date > latest_chapter['date'] or (date == latest_chapter['date'] and chapter_number > latest_chapter['chapter_number']):
            latest_chapter['date'] = date
            latest_chapter['chapter_number'] = chapter_number
            latest_chapter['link'] = link

    latest_chapter['date'] = latest_chapter['date'].strftime('%m/%d/%Y')
    return latest_chapter

############## https://leviatanscans.com ##############
def find_manga_leviatanscans(url, name):
    page = requests.get(url)
    soup = bs(page.content, 'html.parser')
    mangas = []
    className = 'item-thumb c-image-hover'

    results = soup.find_all(class_=className)
    if len(results) <= 0:
        print('nothing')
        return []

    for elem in results:
        link_elem = elem.find('a')
        img_elem = elem.find('img')

        link = link_elem['href']
        manga_name = link_elem['title']
        img_src = img_elem['src']

        if name.lower() in manga_name.lower():
            mangas.append({'link': link, 'img_src': img_src, 'name': manga_name})
    return mangas

def search_leviatanscans(name=''):
    base_url = 'https://leviatanscans.com'
    # New mangas
    url = f'{base_url}/manga/'
    mangas = find_manga_leviatanscans(url, name)

    # Older mangas
    url = f'{base_url}/manga/page/2'
    mangas = mangas + find_manga_leviatanscans(url, name)
    return mangas

def latest_chapter_leviatanscans(url):
    driver = setup_driver()
    driver.get(url)

    try:
        className = 'wp-manga-chapter  '
        # Need to wait for the browser to setup otherwise sometimes it is too fast
        # and results in a "Stale element reference: element is not attached to the page of the document"
        time.sleep(2)
        element = WebDriverWait(driver, 10).until(lambda s: s.find_element(By.CSS_SELECTOR, f'li[class="{className}"]').is_displayed())

        # Page source contents don't get updated for some reason on this page
        # so need to do the parsing using selenium instead of Beautiful soup
        latest_chapter = {'chapter_number': 0, 'date': datetime.datetime.min, 'link': ''}
        results = driver.find_elements(By.CSS_SELECTOR, f'li[class="{className}"]')
        for elem in results:
            link_elem = elem.find_element(By.CSS_SELECTOR, 'a')
            date_elem = elem.find_element(By.CSS_SELECTOR, 'span[class="chapter-release-date"]')
            if link_elem is not None:
                chapter_number = link_elem.text.strip()
                date = date_elem.text.strip()
                # The hidden chapters don't have text, but does are the oldest ones,
                # so no need to worry about them
                if chapter_number is not '' and date is not '':
                    chapter_number = float(chapter_number)
                    link = link_elem.get_attribute('href')
                    date_elem = elem.find_element(By.CSS_SELECTOR, 'span[class="chapter-release-date"]')
                    # Example format: March 20, 2021
                    # Code documentation: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
                    date = datetime.datetime.strptime(date, '%B %d, %Y')

                    if date > latest_chapter['date'] or (date == latest_chapter['date'] and chapter_number > latest_chapter['chapter_number']):
                        latest_chapter['date'] = date
                        latest_chapter['chapter_number'] = chapter_number
                        latest_chapter['link'] = link

        latest_chapter['date'] = latest_chapter['date'].strftime('%m/%d/%Y')

    finally:
        driver.quit()

    return latest_chapter

############## https://reaperscans.com ##############
def get_css_url(css):
    # should be in format url(${url})
    open_paran_index = css.find('(')
    closed_paran_index = css.find(')')

    if open_paran_index == -1 or closed_paran_index == -1:
        return ''

    return css[open_paran_index + 1: closed_paran_index]

def find_manga_reaperscans(soup, name):
    mangas = []
    className = 'list-item'
    results = soup.find_all(class_=className)
    if len(results) <= 0:
        print('nothing')
        return []

    for elem in results:
        title_elem = elem.find('a', class_='list-title')

        manga_name = title_elem.text.strip()
        if name.lower() in manga_name.lower():
            link_elem = elem.find('a', class_='media-content')
            link = link_elem['href']
            # Remove img source since the links are access denied
            #img_src = get_css_url(link_elem['style'])
            mangas.append({'link': link, 'img_src': '', 'name': manga_name})
    return mangas

def search_reaperscans(name=''):
    # Tool for getting through cloudfare captcha
    # If it doesn't work anymore run:
    # pip show cloudscraper -> then if its not the latest version run
    # pip install cloudscraper -U
    # If that doesn't fix it, must find a new tool
    scraper = cloudscraper.create_scraper()
    base_url = 'https://reaperscans.com/comics'

    url = f'{base_url}?page=1'
    soup = bs(scraper.get(url).text, 'html.parser')

    pagination_elem = soup.find('ul', class_='pagination')
    pagination_items = pagination_elem.find_all('li', class_='page-item')
    # Subtract 2 for the before and after arrow
    page_count = len(pagination_items) - 2
    mangas = find_manga_reaperscans(soup, name)
    for i in range(2, page_count + 1):
        url = f'{base_url}?page={i}'
        soup = bs(scraper.get(url).text, 'html.parser')
        mangas = mangas + find_manga_reaperscans(soup, name)
    return mangas

def time_diff_to_date(time):
    num = float(''.join(i for i in time if i.isdigit() or i is '.'))
    today = datetime.datetime.now()
    diff = relativedelta(seconds=0)
    if 'seconds' in time:
        diff = relativedelta(seconds=num)
    elif 'minutes' in time:
        diff = relativedelta(minutes=num)
    elif 'hour' in time:
        diff = relativedelta(hours=num)
    elif 'day' in time:
        diff = relativedelta(days=num)
    elif 'week' in time:
        diff = relativedelta(weeks=num)
    elif 'month' in time:
        diff = relativedelta(months=num)
    elif 'year' in time:
        diff = relativedelta(years=num)
    else:
        pass
    return today - diff

def latest_chapter_reaperscans(url):
    # Tool for getting through cloudfare captcha
    # If it doesn't work anymore run:
    # pip show cloudscraper -> then if its not the latest version run
    # pip install cloudscraper -U
    # If that doesn't fix it, must find a new tool
    scraper = cloudscraper.create_scraper()
    soup = bs(scraper.get(url).text, 'html.parser')
    className = 'list-item col-sm-3 no-border'
    results = soup.find_all(class_=className)
    if len(results) <= 0:
        return []
    latest_chapter = {'chapter_number': 0, 'date': datetime.datetime.min, 'link': ''}
    for elem in results:
        chapter_number_elem = elem.find('span')
        link_elem = elem.find('a', class_='item-company')

        chapter_number = float(chapter_number_elem.text.strip())
        link = link_elem['href']
        date = time_diff_to_date(link_elem.text.strip())

        if date > latest_chapter['date'] or (date == latest_chapter['date'] and chapter_number > latest_chapter['chapter_number']):
            latest_chapter['date'] = date
            latest_chapter['chapter_number'] = chapter_number
            latest_chapter['link'] = link

    latest_chapter['date'] = latest_chapter['date'].strftime('%m/%d/%Y')
    return latest_chapter