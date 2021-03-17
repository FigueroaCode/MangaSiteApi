import json

def test_mangalife_search(app, client):
    res = client.get(f'/search/manga4life.com/slime tao')
    assert res.status_code == 200

def test_mangalife_latest_chapter(app, client):
    res = client.get(f'/latest_chapter/manga4life.com/https://manga4life.com/manga/Martial-Peak')
    assert res.status_code == 200