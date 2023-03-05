from flaskr import create_app

import pytest

# See https://flask.palletsprojects.com/en/2.2.x/testing/ 
# for more info on testing
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# TODO(Checkpoint (groups of 4 only) Requirement 4): Change test to
# match the changes made in the other Checkpoint Requirements.
def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Welcome To Our Wiki-fun in your local\n" in resp.data

# TODO(Project 1): Write tests for other routes.
def test_about_page(client):
    resp = client.get('/about')
    assert resp.status_code == 200
    assert b"Manish" in resp.data
    assert b"Gabriel" in resp.data
    assert b"Myles" in resp.data

def test_pages_page(client):
    resp = client.get('/pages')
    assert resp.status_code == 200
    # Check we are getting only the name of the pages, and not their file extensions.
    assert b"GeorgeTown Waterfront Park" in resp.data
    assert b"GeorgeTown Waterfront Park.txt" not in resp.data
    # Check we are only getting text files.
    assert b"gabrielPic" not in resp.data





    