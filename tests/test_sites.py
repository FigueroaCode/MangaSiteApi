import json

def test_mangalife_search(app, client):
    res = client.get(f'/search/manga4life.com/slime tao')
    assert res.status_code == 200

def test_manganelo_search(app, client):
    res = client.get(f'/search/manganelo.com/the beginning')
    assert res.status_code == 200

def test_leviatanscans_search(app, client):
    res = client.get(f'/search/leviatanscans.com/sorcerer king')
    assert res.status_code == 200

def test_mangalife_latest_chapter(app, client):
    res = client.get(f'/latest_chapter/manga4life.com/https://manga4life.com/manga/Martial-Peak')
    assert res.status_code == 200

def test_manganelo_latest_chapter(app, client):
    res = client.get(f'/latest_chapter/manganelo.com/https://manganelo.com/manga/ijhr296321559609648')
    assert res.status_code == 200

def test_leviatanscans_latest_chapter(app, client):
    res = client.get(f'/latest_chapter/leviatanscans.com/https://leviatanscans.com/manga/the-legend-of-sura-venom-dragon/')
    assert res.status_code == 200

def test_reaperscans_search(app, client):
    res = client.get(f'/search/reaperscans.com/xiu tu')
    assert res.status_code == 200

def test_reaperscans_latest_chapter(app, client):
    res = client.get(f'/latest_chapter/reaperscans.com/https://reaperscans.com/comics/316621-the-great-mage-returns-after-4000-years')
    assert res.status_code == 200

def test_latest(app, client):
    manga_data = {
        'mangas': [
            {
                'img_src': 'https://cover.nep.li/cover/Tensei-Shitara-Slime-Datta-Ken.jpg',
                'last_read': 0,
                'link': 'https://manga4life.com/manga/Tensei-Shitara-Slime-Datta-Ken',
                'name': 'Tensei Shitara Slime Datta Ken',
                'source': 'manga4life.com',
                'release_date': '',
                'chapter_link': '',
                'latest_chapter': 0
            },
            {
                'img_src': 'https://leviatanscans.com/wp-content/uploads/2021/03/cover_MLHWR-110x150.png',
                'last_read': 0,
                'link': 'https://leviatanscans.com/manga/the-max-leveled-hero-will-return/',
                'name': 'The Max Leveled Hero Will Return!',
                'source': 'leviatanscans.com',
                'release_date': '',
                'chapter_link': '',
                'latest_chapter': 0
            },
            {
                'img_src': '',
                'last_read': 0,
                'link': 'https://reaperscans.com/comics/777794-demonic-emperor',
                'name': 'Demonic Emperor',
                'source': 'reaperscans.com',
                'release_date': '',
                'chapter_link': '',
                'latest_chapter': 0
            },
        ]    
    }
    res = client.post(f'/latest', data=json.dumps(manga_data))
    assert res.status_code == 200