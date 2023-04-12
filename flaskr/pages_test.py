from flaskr import create_app
from flaskr.backend import User ,Backend
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
    with patch('flaskr.backend.Backend.get_all_page_names') as mock_page:
        mock_page.return_value = ['Page 1','Page 2']
        resp = client.get('/pages')
        assert resp.status_code == 200
        assert b"Page 1" in resp.data
        assert b"Page 2" in resp.data


def test_wiki_page(client):
    with patch('flaskr.backend.Backend.get_wiki_page') as mock_page:
            mock_page.return_value = json.loads('{"wiki_page": "really_fake_page", "content": "really_fake_content", "date_created": "0000-00-00", "upvotes": 0, "who_upvoted": null, "downvotes": 0, "who_downvoted": null, "comments": []}')
    
            resp = client.get('/pages/GeorgeTown%20Waterfront%20Park')
            assert resp.status_code == 200
            assert b"really_fake_content" in resp.data 


def test_login(client, test_user):
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


def test_login_incorrect_password(client, test_user):
    # If we pass the wrong information, we will not be redirected.
    with patch('flaskr.backend.Backend.sign_in') as mock_login:
        mock_login.return_value = None 
        response = client.post('/login',
                            data={
                                'username':'fake_username',
                                'password': 'wrongpassword'
                            })
    assert response.status_code == 200
    # We do not have a user authenticated as nobody actually logged in.
    assert current_user.is_authenticated == False
    assert b'Invalid username or password' in response.data


def test_logout(client, test_user):


    # login_user(User('fake_username'))
    response = client.get('/logout')
    print(response.data)
    assert response.status_code == 302
    assert current_user.is_authenticated == False


def test_signup(client, test_user):
    # Send a response to the route trying to verify for the test user.
    with patch('flaskr.backend.Backend.sign_up') as mock_signup:
        with patch('flaskr.backend.Backend.sign_in') as mock_signin:

        
            mock_signup.return_value = True
            mock_signin.return_value = User('new_user')
            response = client.post('/signup',
                                data={
                                    'username': 'new_user',
                                    'password': 'new_user'
                                })
            # We should get redirected to the home page, resulting in a 302 code.
            assert response.status_code == 302
            # The current_user should be updated to 'testing'.
            assert current_user.username == 'new_user'


def test_incorrect_signup(client, test_repeatuser):
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
        data = {'file': (io.BytesIO(b'my file contents'),'fake_file.txt'),'filename': 'fake_file.txt'}
         # Open the file in binary mode
        response = client.post('/upload', data =data)    

        assert response.status_code == 200
        assert b'Uploaded Successfully' in response.data


def test_search_for_title_with_results(client):

    ''' Testing the search route for search_by_title post with some results 

          Args : 
            client : Flask Client Object 

    '''
    with patch('flaskr.backend.Backend.search_by_title') as mock_search:

        mock_search.return_value = ['title_1','title_2']
        response = client.post('/search' ,data={'search_query':'query' , 'search_by':'title'})
        assert response.status_code == 200
        assert b'title_1' in response.data
        assert b'title_2' in response.data

    mock_search.assert_called_once_with('query')

    

def test_search_for_title_with_no_result(client):

    ''' Testing the search route for search_by_title post for  empty list 

         Args : 
            client : Flask Client Object 

    '''
    with patch('flaskr.backend.Backend.search_by_title') as mock_search:
        mock_search.return_value = []
        response=client.post('/search',data={'search_query':'query', 'search_by' : 'title'})

        assert response.status_code == 200
        assert b'No such pages found for' in response.data

    
def test_search_for_content_with_results(client):
    '''  Testing the search rout for search_by_content post with some results

        Args : 
            client : Flask Client Object 
    ''' 
    with patch('flaskr.backend.Backend.search_by_content') as mock_search:
        mock_search.return_value = ['title_3' ,'title_4']

        # print(Backend.search_by_content())
        response=client.post('/search',data={'search_query':'query', 'search_by' : 'content'})
      
        assert response.status_code == 200
        assert b'title_3' in response.data
        assert b'title_4' in response.data
        
def test_search_for_content_with_no_result(client):
    '''  Testing the search route for search_by_content post with some results

        Args : 
            client : Flask Client Object 
    ''' 
    with patch('flaskr.backend.Backend.search_by_content') as mock_search:

        mock_search.return_value = []
        response=client.post('/search',data={'search_query':'query', 'search_by' : 'content'})
      
        assert response.status_code == 200
        assert b'No such pages found with ' in response.data

def test_page_commenting(client):
    '''  Testing the post comment in page route 

        Args : 
          client : Flask Client Object 
    '''

        # Patch the backend method for update page.
    with patch('flaskr.backend.Backend.get_wiki_page') as mock_page:
        mock_page.return_value = json.loads(
            '{"wiki_page": "fake_page", "content": "fake_content", "date_created": "0000-00-00", "upvotes": 0, "who_upvoted": null, "downvotes": 0, "who_downvoted": [], "comments": []}'
        )

        # Patch the backend method for update page.
        with patch('flaskr.backend.Backend.updating_metadata_with_comments') as mock_update_comment:

            # Also patch the flask_login current_user module; replace with a fake user.
            with patch('flaskr.pages.current_user', User('fake_user')):

                #sample how it looks like after calling 
                fake_metadata = {
                    "wiki_page": "fake_page",
                    "content": "fake_content",
                    "date_created": "0000-00-00",
                    "upvotes": 0,
                    "who_upvoted": None,
                    "downvotes": 0,
                    "who_downvoted": [],
                    "comments": [{'fake_userr': 'fake_comment'}]

                }

                response = client.post('/pages/fake_page',
                                   data={'post_button': 'post' , 'user_comment' : 'fake_comment'})

                assert response.status_code == 302

                mock_update_comment.assert_called_once_with("fake_page", "fake_user", "fake_comment")
                

def test_page_commenting_without_user(client):
    ''' Testing the post comment when user is not logged in 

        Args : 
            Client : Flask Client Object 
    '''

    with patch('flaskr.backend.Backend.get_wiki_page') as mock_page:
        mock_page.return_value = json.loads(
            '{"wiki_page": "fake_page", "content": "fake_content", "date_created": "0000-00-00", "upvotes": 0, "who_upvoted": null, "downvotes": 0, "who_downvoted": [], "comments": []}'
        )

        # Make a POST request to the endpoint without an authenticated user.
        resp = client.post('/pages/fake_page', data={'post_button': 'post'}) # no user 

        assert resp.status_code == 200
        assert b'Please login or signup to make a comment' in resp.data



        
