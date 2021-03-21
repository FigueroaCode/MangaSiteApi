from app import app, sites
from flask import request
from selenium.common.exceptions import TimeoutException
import datetime
import sys
import json

@app.route('/')
def home():
    #sites.latest_chapter_mangalife('https://manga4life.com/manga/Slime-Taoshite-300-nen-Shiranai-Uchi-Ni-Level-Max-Ni-Nattemashita')
    return 'Hello World!';

@app.route('/search/<string:sitename>/<string:name>')
def search(sitename, name):
    try:
        mangas = []
        if sitename == 'manga4life.com':
            mangas = sites.search_mangalife(name)

        return {'mangas': mangas}, 200
    except TimeoutException:
        print('Error: Could not find tag within time limit')
        return {'mangas': []}, 500
    except Exception as e:
        print(e)
        return {'mangas': []}, 500

@app.route('/latest', methods=['GET', 'POST'])
def latest():
    data = json.loads(request.data)
    mangas = data['mangas']
    return sites.latest_chapters(mangas)

@app.route('/latest_chapter/<string:sitename>/<path:manga_url>')
def latest_chapter(sitename, manga_url):
    try:
        chapter = {'chapter_number': 0, 'date': datetime.datetime.min, 'link': ''}
        if sitename == 'manga4life.com':
            chapter = sites.latest_chapter_mangalife(manga_url)

        return {'latest_chapter': chapter}, 200
    except TimeoutException:
        print('Error: Could not find tag within time limit')
        return {'latest_chapter': {}}, 500
    except Exception as e:
        print(e)
        return {'latest_chapter': {}}, 500