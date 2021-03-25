import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from bs4 import BeautifulSoup as bs
from urllib.parse import quote, urlencode
import datetime
from dateutil.relativedelta import relativedelta
import time
import concurrent.futures
import chromedriver_binary  # Adds chromedriver binary to path


'''
    https://zeroscans.com/home
DONE    https://manga4life.com/
    https://leviatanscans.com/
    https://lhtranslation.net/
    https://mangasushi.net/
    https://manhuaplus.com/
    https://mangadex.org/
    https://manganelo.com/
DONE    https://reaperscans.com/home
'''
#
# For formatting the html: https://www.freeformatter.com/html-formatter.html#ad-output
# Set to true to save the html of the requested page
SAVE_OUTPUT = False
MAX_THREADS = 30

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

def save_page(page):    
    with open('output.html', 'w',  encoding="utf-8") as file:
        file.write(page.page_source)

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
                name = elem2.text.strip()
                img_src = img_elem['src']
                mangas.append({'link': link, 'img_src': img_src, 'name': name})
            else:
                img_elem = elem2.find('img')
                link = base_url + elem2['href']
                name = elem1.text.strip()
                img_src = img_elem['src']
                mangas.append({'link': link, 'img_src': img_src, 'name': name})
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
                    prev = '0'
                    number = []
                    for i in span.text.strip():
                        if i.isdigit() or (prev.isdigit() and i is '.'):
                            number.append(i)
                        prev = i
                    chapter_number = float(''.join(number))

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

def find_manga_reaperscans(driver, soup, name):
    mangas = []
    className = 'list-item'
    # Need to wait for the browser to setup otherwise sometimes it is too fast
    # and results in a "Stale element reference: element is not attached to the page of the document"
    time.sleep(1)
    element = WebDriverWait(driver, 5).until(lambda s: s.find_element_by_class_name(className).is_displayed())

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
    base_url = 'https://reaperscans.com/comics'
    driver = setup_driver()

    try:
        url = f'{base_url}?page=1'
        driver.get(url)
        pagination_elem = WebDriverWait(driver, 5).until(lambda s: s.find_element_by_class_name('pagination').is_displayed())
        soup = bs(driver.page_source, 'html.parser')

        pagination_elem = soup.find('ul', class_='pagination')
        pagination_items = pagination_elem.find_all('li', class_='page-item')
        # Subtract 2 for the before and after arrow
        page_count = len(pagination_items) - 2
        mangas = find_manga_reaperscans(driver, soup, name)
        for i in range(2, page_count + 1):
            url = f'{base_url}?page={i}'
            driver.get(url)
            soup = bs(driver.page_source, 'html.parser')
            mangas = mangas + find_manga_reaperscans(driver, soup, name)

    finally:
        driver.quit()

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
    driver = setup_driver()
    driver.get(url)

    if SAVE_OUTPUT:
        save_page(driver)
    try:
        className = 'list-item col-sm-3 no-border'
        # Need to wait for the browser to setup otherwise sometimes it is too fast
        # and results in a "Stale element reference: element is not attached to the page of the document"
        time.sleep(2)
        element = WebDriverWait(driver, 5).until(lambda s: s.find_element(By.CSS_SELECTOR, f'div[class="{className}"]').is_displayed())

        soup = bs(driver.page_source, 'html.parser')

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

    finally:
        driver.quit()

    return latest_chapter

############## General ##############
def update_manga(manga):
    latest_chapter = {'chapter_number': 0, 'date': 'Failed to get data', 'link': manga['link']}

    if manga['source'] == 'manga4life.com':
        latest_chapter = latest_chapter_mangalife(manga['link'])
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