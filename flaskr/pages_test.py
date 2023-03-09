from flaskr import create_app
from flaskr.backend import User
from flask import Flask, session
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

import pytest

# See https://flask.palletsprojects.com/en/2.2.x/testing/ 
# for more info on testing
@pytest.fixture
def app():

    login_manager = LoginManager()

    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'mysecretkey',
        'WTF_CSRF_ENABLED': False
    })
    
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_id(user_id)

    return app

@pytest.fixture
def client(app):
    client = app.test_client()
    return client

@pytest.fixture
def user_id():
    return 'testuser'

@pytest.fixture
def user_password():
    return 'testpassword'

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

def test_wiki_page(client):
    resp = client.get('/pages/GeorgeTown%20Waterfront%20Park')
    assert resp.status_code == 200
    
    # Check we are getting the information contained inside the text file.
    assert b"GEORGETOWN WATERFRONT PARK" in resp.data
    assert b"Located along the banks of the Potomac," in resp.data

def test_wiki_page_failure(client):
    resp = client.get('/pages/NonExistingPage')
    assert resp.status_code == 404

@pytest.fixture
def authenticated_client(client, user_id, user_password):
    # Log in the user for testing
    with client:
        response = client.post('/login', data=dict(
            username=user_id,
            password=user_password
        ), follow_redirects=True)
        assert response.status_code == 200
        assert current_user.is_authenticated
        yield client
        # Log out the user after testing
        logout_user()

def test_login(client, user_id, user_password):
    # Log in the user
    response = client.post('/login', data=dict(
        username=user_id,
        password=user_password
    ), follow_redirects=True)
    
    # Check that the login was successful
    assert response.status_code == 200
    assert current_user.is_authenticated

def test_logout(authenticated_client):
    # Log out the user
    response = authenticated_client.get('/logout', follow_redirects=True)

    # Check that the logout was successful
    assert response.status_code == 200
    assert not current_user.is_authenticated
