from app import app, sites
from flask import request
from selenium.common.exceptions import TimeoutException
import datetime
import sys
import json

@app.route('/')
def home():
    return 'Hello World!';

@app.route('/latest', methods=['GET', 'POST'])
def latest():
    data = json.loads(request.data)
    mangas = data['mangas']
    try:
        latest_chapters = sites.latest_chapters(mangas)
        return {'mangas': latest_chapters}, 200
    except TimeoutException:
        print('Error: Could not find tag within time limit')
        return {'error': 'Error: Could not find tag within time limit'}, 500
    except Exception as e:
        print(e)
        return {'error': str(e)}, 500

@app.route('/search/<string:sitename>/<string:name>')
def search(sitename, name):
    try:
        mangas = []
        if sitename == 'manga4life.com':
            mangas = sites.search_mangalife(name)
        elif sitename == 'reaperscans.com':
            mangas = sites.search_reaperscans(name)

        return {'mangas': mangas}, 200
    except TimeoutException:
        print('Error: Could not find tag within time limit')
        return {'error': 'Error: Could not find tag within time limit'}, 500
    except Exception as e:
        print(e)
        return {'error': str(e)}, 500

@app.route('/latest_chapter/<string:sitename>/<path:manga_url>')
def latest_chapter(sitename, manga_url):
    try:
        chapter = {'chapter_number': 0, 'date': datetime.datetime.min, 'link': ''}
        if sitename == 'manga4life.com':
            chapter = sites.latest_chapter_mangalife(manga_url)
        elif sitename == 'reaperscans.com':
            chapter = sites.latest_chapter_reaperscans(manga_url)

        return {'latest_chapter': chapter}, 200
    except TimeoutException:
        print('Error: Could not find tag within time limit')
        return {'error': 'Error: Could not find tag within time limit'}, 500
    except Exception as e:
        print(e)
        return {'error': str(e)}, 500