import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup as bs
from urllib.parse import quote, urlencode
import datetime

import chromedriver_binary  # Adds chromedriver binary to path

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

# For formatting the html: https://www.freeformatter.com/html-formatter.html#ad-output
# Set to true to save the html of the requested page
SAVE_OUTPUT = False
def save_page(page):    
    with open('output.html', 'w',  encoding="utf-8") as file:
        file.write(page.page_source)

############## https://manga4life.com/ ##############
# TODO: Search on site (2 forms: use site's search, get all manga in site and search manually)
# TODO: Check if given manga has updated

def search_mangalife(name=''):
    base_url = 'https://manga4life.com'
    url = f'{base_url}/search/?'
    params = {'name': name}
    url += urlencode(params, quote_via=quote)

    driver = setup_driver()
    driver.get(url)
    
    try:
        className = 'SeriesName'
        element = WebDriverWait(driver, 1).until(lambda s: s.find_element_by_class_name(className).is_displayed())
        if SAVE_OUTPUT:
            save_page(driver)
        soup = bs(driver.page_source, 'html.parser')

        results = soup.find_all(class_=className)
        if len(results) <= 0:
            print('nothing')
            return []

        mangas = []
        for elem in results:
            link = base_url + elem['href']
            img_elem = elem.find('img')
            img_src = ''
            if img_elem is not None:
                img_src = img_elem['src']

            mangas.append({'link': link, 'img_src': img_src})

    except TimeoutException:
        print("TimeoutException: Element not found")
        raise
    finally:
        driver.quit()

    return mangas
    
def latest_chapter_mangalife(url):
    driver = setup_driver()
    driver.get(url)
    try:
        className = 'ChapterLink'
        element = WebDriverWait(driver, 1).until(lambda s: s.find_element_by_class_name(className).is_displayed())
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
                    chapter = span.text.strip()
                    chapter_number = float(''.join(i for i in chapter if i.isdigit() or i is '.'))

            if date > latest_chapter['date'] or (date == latest_chapter['date'] and chapter_number > latest_chapter['chapter_number']):
                latest_chapter['date'] = date
                latest_chapter['chapter_number'] = chapter_number
                latest_chapter['link'] = link

        latest_chapter['date'] = latest_chapter['date'].strftime('%m/%d/%Y')
    finally:
        driver.quit()

    return latest_chapter