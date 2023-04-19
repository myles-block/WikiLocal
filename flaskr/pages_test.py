from flaskr import create_app
from flaskr.backend import User, Backend
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from unittest.mock import patch
import pytest
import base64
import json
import io


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


# TODO(Checkpoint (groups of 4 only) Requirement 4): Change test to
# match the changes made in the other Checkpoint Requirements.
def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Welcome To Our Wiki-fun in your local\n" in resp.data


# TODO(Project 1): Write tests for other routes.
def test_about_page(client):
    '''  Test function to test about route 

        Arg : Client 
    '''

    with patch('flaskr.backend.Backend.get_image') as mock_get_image:

        expected = base64.b64encode(b'Fake_Image_Data').decode('utf-8')
        mock_get_image.return_value = expected
        response = client.get('/about')

        assert response.status_code == 200
        expected_html = f"<img src='data:image/jpeg;base64,{expected}' alt='Author Image'>"
        assert expected_html.encode() in response.data


def test_pages_page(client):
    '''  Test function to test '/pages' route 

        Arg : Client 
    '''

    # Patch the get_all_page_names method from the backend so we don't call GCS
    with patch('flaskr.backend.Backend.get_all_page_names') as mock_page:
        mock_page.return_value = [['Page 1', 12, 0], ['Page 2', 1, 6]]

        resp = client.get('/pages')

        # Check that the request succeeds and both the page name and ratings are displayed.
        assert resp.status_code == 200
        assert b"Page 1" in resp.data
        assert b"Page 2" in resp.data
        assert b"6" in resp.data
        assert b"12" in resp.data


def test_wiki_page(client):
    '''  Test function to test the parameterised '/pages/<page_name>' route 

        Arg : Client 
    '''

    # Patch the get_wiki_page method so we don't call GCS
    with patch('flaskr.backend.Backend.get_wiki_page') as mock_page:
        with patch('flaskr.backend.Backend.update_wikihistory'
                  ) as mock_update_wikihistory:
            mock_update_wikihistory.return_value = None
            mock_page.return_value = json.loads(
                '{"wiki_page": "really_fake_page", "content": "really_fake_content", "date_created": "0000-00-00", "upvotes": 0, "who_upvoted": [], "downvotes": 0, "who_downvoted": [], "comments": []}'
            )

            resp = client.get('/pages/GeorgeTown%20Waterfront%20Park')

            assert resp.status_code == 200
            assert b"really_fake_content" in resp.data


def test_wiki_page_with_comments(client):
    '''  Test function to test the parameterised '/pages/<page_name>' route 
         when it has comments.
        Arg : Client 
    '''

    # Patch the get_wiki_page method so we don't call GCS
    with patch('flaskr.backend.Backend.get_wiki_page') as mock_page:
        mock_page.return_value = json.loads(
            '{"wiki_page": "really_fake_page", "content": "really_fake_content", "date_created": "0000-00-00", "upvotes": 0, "who_upvoted": [], "downvotes": 0, "who_downvoted": [], "comments": [{"fake_commenter": "This is a fake comment"}]}'
        )

        resp = client.get('/pages/GeorgeTown%20Waterfront%20Park')

        # Check the request succeeds and the both the comment's author and content are displayed.
        assert resp.status_code == 200
        assert b"fake_commenter" in resp.data
        assert b"This is a fake comment" in resp.data


def test_login(client):
    # Send a response to the route trying to verify for the test user.
    with patch('flaskr.backend.Backend.sign_in') as mock_login:
        mock_login.return_value = User('fake_username')
        # print(Backend.sign_in())
        response = client.post('/login',
                               data={
                                   'username': 'fake_username',
                                   'password': 'testing'
                               })
        # We should get redirected to the home page, resulting in a 302 code.
        assert response.status_code == 302
        # The current_user should be updated to 'testing'.
        assert current_user.username == 'fake_username'


def test_login_incorrect_password(client):
    # If we pass the wrong information, we will not be redirected.
    with patch('flaskr.backend.Backend.sign_in') as mock_login:
        mock_login.return_value = None
        response = client.post('/login',
                               data={
                                   'username': 'fake_username',
                                   'password': 'wrongpassword'
                               })
    assert response.status_code == 200
    # We do not have a user authenticated as nobody actually logged in.
    assert current_user.is_authenticated == False
    assert b'Invalid username or password' in response.data


def test_logout(client):

    # login_user(User('fake_username'))
    response = client.get('/logout')
    print(response.data)
    assert response.status_code == 302
    assert current_user.is_authenticated == False


def test_signup(client):
    # Send a response to the route trying to verify for the test user.
    with patch('flaskr.backend.Backend.sign_up') as mock_signup:

        mock_signup.return_value = User('new_user')
        response = client.post('/signup',
                               data={
                                   'username': 'new_user',
                                   'password': 'new_user'
                               })
        # We should get redirected to the home page, resulting in a 302 code.
        assert response.status_code == 302
        # The current_user should be updated to 'testing'.
        assert current_user.username == 'new_user'


def test_incorrect_signup(client):
    # Send a response to the route trying to hit the same user.

    with patch('flaskr.backend.Backend.sign_up') as mock_signup:

        mock_signup.return_value = False
        response = client.post('/signup',
                               data={
                                   'username': 'new_user',
                                   'password': 'new_user'
                               })
        # We should get redirected to the home page, resulting in a 302 code.
        assert response.status_code == 200
        # The current_user should be updated to 'testing'.
        assert current_user.is_authenticated == False
    # We should not go to the home page, resulting in a 200 code.


def fixit_test_upload(client):

    with patch('flaskr.backend.Backend.upload') as mock_upload:

        mock_upload.return_value = None
        data = {
            'file': (io.BytesIO(b'my file contents'), 'fake_file.txt'),
            'filename': 'fake_file.txt'
        }
        # Open the file in binary mode
        response = client.post('/upload', data=data)

        assert response.status_code == 200
        assert b'Uploaded Successfully' in response.data


def test_wiki_page_upvote(client):
    ''' Testing the wiki_page route for a wiki page with one upvote.
         Args : 
            client : Flask Client Object 
    '''

    # Patch the get_wiki_page method
    with patch('flaskr.backend.Backend.get_wiki_page') as mock_page:
        mock_page.return_value = json.loads(
            '{"wiki_page": "really_fake_page", "content": "really_fake_content", "date_created": "0000-00-00", "upvotes": 1, "who_upvoted": ["some_fake_user"], "downvotes": 0, "who_downvoted": [], "comments": []}'
        )

        # Patch the backend method for update page.
        with patch('flaskr.backend.Backend.update_page') as mock_update:

            # Also patch the flask_login current_user module; replace with a fake user.
            with patch('flaskr.pages.current_user', User('some_fake_user')):
                with patch('flaskr.backend.Backend.update_wikihistory'
                          ) as mock_update_wikihistory:
                    mock_update_wikihistory.return_value = None
                    # Mock the update_page method by making it return a dictionary representing wiki page metadata.
                    mock_update.return_value = {
                        "wiki_page": "really_fake_page",
                        "content": "really_fake_content",
                        "date_created": "0000-00-00",
                        "upvotes": 1,
                        "who_upvoted": ['some_fake_user'],
                        "downvotes": 0,
                        "who_downvoted": [],
                        "comments": []
                    }

                    resp = client.post('/pages/testingmetadata',
                                       data={'submit_button': 'Yes!'})

                    # Assert the request succeeds and the vote count is reflected.
                    assert resp.status_code == 302
                    assert b"1" in resp.data


def test_wiki_page_downvotes(client):
    ''' Testing the pages parameterised route for a wiki page with two downvotes
         Args : 
            client : Flask Client Object 
    '''

    # Patch the get_wiki_page method
    with patch('flaskr.backend.Backend.get_wiki_page') as mock_page:
        mock_page.return_value = json.loads(
            '{"wiki_page": "really_fake_page", "content": "really_fake_content", "date_created": "0000-00-00", "upvotes": 0, "who_upvoted": [], "downvotes": 2, "who_downvoted": ["some_fake_user", "another_fake_user"], "comments": []}'
        )

        # Patch the backend method for update page.
        with patch('flaskr.backend.Backend.update_page') as mock_update:

            # Also patch the flask_login current_user module; replace with a fake user.

            with patch('flaskr.pages.current_user', User('some_fake_user')):
                with patch('flaskr.backend.Backend.update_wikihistory'
                          ) as mock_update_wikihistory:
                    mock_update_wikihistory.return_value = None
                    # Mock the update_page method by making it return a dictionary representing wiki page metadata.
                    mock_update.return_value = {
                        "wiki_page": "really_fake_page",
                        "content": "really_fake_content",
                        "date_created": "0000-00-00",
                        "upvotes": 0,
                        "who_upvoted": [],
                        "downvotes": 2,
                        "who_downvoted": [
                            'some_fake_user', 'another_fake_user'
                        ],
                        "comments": []
                    }

                    resp = client.post('/pages/testingmetadata',
                                       data={'submit_button': 'Nope'})

                    # Assert the request succeeds and the vote count is reflected.
                    assert resp.status_code == 302
