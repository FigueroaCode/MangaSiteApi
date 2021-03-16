import json

def test_mangalife_search(app, client):
    res = client.get(f'/search/manga4life/slime tao')
    assert res.status_code == 200

def test_mangalife_latest_chapter(app, client):
    res = client.get(f'/')
    assert res.status_code == 200