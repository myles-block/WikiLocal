from flaskr import create_app
from flaskr.backend import User
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

import pytest


# See https://flask.palletsprojects.com/en/2.2.x/testing/
# for more info on testing
@pytest.fixture
def app():

    app = create_app({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
    })

    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def test_user():
    username = 'testing'
    password = 'testing'
    user = User(username)
    # Upload a test user to the bucket.
    user.save(password)
    yield user
    blob = user.bucket.blob(username)
    # After we have finished testing, just delete it.
    blob.delete()


@pytest.fixture
def test_newuser():
    username = 'new_user'
    password = 'new_user'
    user = User(username)
    # Upload a test user to the bucket.
    user.save(password)
    yield user
    blob = user.bucket.blob(username)
    # After we have finished testing, just delete it.
    blob.delete()


@pytest.fixture
def test_repeatuser():
    username = 'new_user_same'
    password = 'new_user'
    user = User(username)
    # Upload a test user to the bucket.
    user.save(password)
    yield user
    # blob = user.bucket.blob(username)


# TODO(Checkpoint (groups of 4 only) Requirement 4): Change test to
# match the changes made in the other Checkpoint Requirements.
def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Welcome To Our Wiki-fun in your local\n" in resp.data


# TODO(Project 1): Write tests for other routes.
def fixit_test_about_page(client):
    resp = client.get('/about')
    assert resp.status_code == 200
    assert b"Manish" in resp.data
    assert b"Gabriel" in resp.data
    assert b"Myles" in resp.data


def fixit_test_pages_page(client):
    resp = client.get('/pages')
    assert resp.status_code == 200
    # Check we are getting only the name of the pages, and not their file extensions.
    assert b"GeorgeTown Waterfront Park" in resp.data
    assert b"GeorgeTown Waterfront Park.txt" not in resp.data
    # Check we are only getting text files.
    assert b"gabrielPic" not in resp.data


def fixit_test_wiki_page(client):
    resp = client.get('/pages/GeorgeTown%20Waterfront%20Park')
    assert resp.status_code == 200

    # Check we are getting the information contained inside the text file.
    assert b"GEORGETOWN WATERFRONT PARK" in resp.data
    assert b"Located along the banks of the Potomac," in resp.data


def fixit_test_login(client, test_user):
    # Send a response to the route trying to verify for the test user.
    response = client.post('/login',
                           data={
                               'username': 'testing',
                               'password': 'testing'
                           })
    # We should get redirected to the home page, resulting in a 302 code.
    assert response.status_code == 302
    # The current_user should be updated to 'testing'.
    assert current_user.username == 'testing'


def fixit_test_login_incorrect_password(client, test_user):
    # If we pass the wrong information, we will not be redirected.
    response = client.post('/login',
                           data={
                               'username': 'testing',
                               'password': 'wrongpassword'
                           })
    assert response.status_code == 200
    # We do not have a user authenticated as nobody actually logged in.
    assert current_user.is_authenticated == False


def fixit_test_logout(client, test_user):
    response = client.post('/login',
                           data={
                               'username': 'testing',
                               'password': 'testing'
                           })
    assert response.status_code == 302
    assert current_user.is_authenticated
    assert current_user.username == 'testing'

    # Check if logging out actually works
    response = client.get('/logout')
    assert response.status_code == 302
    assert current_user.is_anonymous


def fixit_test_signup(client, test_user):
    # Send a response to the route trying to verify for the test user.
    response = client.post('/signup',
                           data={
                               'username': 'new_user',
                               'password': 'new_user'
                           })
    # We should get redirected to the home page, resulting in a 302 code.
    assert response.status_code == 302
    # The current_user should be updated to 'testing'.
    assert current_user.username == 'new_user'


def fixit_test_incorrect_signup(client, test_repeatuser):
    # Send a response to the route trying to hit the same user.
    response = client.post('/signup',
                           data={
                               'username': 'new_user_same',
                               'password': 'new_user'
                           })
    # We should not go to the home page, resulting in a 200 code.
    assert response.status_code == 200  
