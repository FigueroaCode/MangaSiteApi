from app import app, sites
from selenium.common.exceptions import TimeoutException

@app.route('/')
def home():
    #sites.latest_chapter_mangalife('https://manga4life.com/manga/Slime-Taoshite-300-nen-Shiranai-Uchi-Ni-Level-Max-Ni-Nattemashita')
    return 'Hello World!';

@app.route('/search/<sitename>/<name>')
def search(sitename, name):
    try:
        mangas = []
        if sitename == 'manga4life':
            mangas = sites.search_mangalife(name)

        return {'mangas': mangas}, 200
    except TimeoutException:
        return {'mangas': []}, 500