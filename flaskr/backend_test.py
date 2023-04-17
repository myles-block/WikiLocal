from flaskr.backend import Backend, User
from unittest.mock import MagicMock, patch
import pytest
import base64
import hashlib
import json
import io
from freezegun import freeze_time


# TODO(Project 1): Write tests for Backend methods.
@pytest.fixture
def fake_blob():
    ''' mocking the blob object as it is one of the dependency on the backend class'''

    return MagicMock()


@pytest.fixture
def bucket(fake_blob):
    ''' mocking the bucket injecting fake_blob '''

    bucket = MagicMock()
    bucket.blob.return_value = fake_blob  # returns the value of fake_blob
    return bucket


@pytest.fixture
def fake_client():
    return MagicMock()


@pytest.fixture
def backend(bucket, fake_client):
    backend = Backend(storage_client=fake_client)
    backend.info_bucket = bucket
    backend.user_bucket = bucket
    return backend


def test_get_all_pages(backend, fake_client, fake_blob):

    # Setting blob's name property
    fake_blob.name = 'Example Blob.txt'

    # Mocking listing all the blobs of a bucket.
    fake_client.list_blobs.return_value = [fake_blob]

    # Calling the actual function with the mock data.
    result = backend.get_all_page_names()
    expected = ['Example Blob']

    # Are we getting what we want?
    assert result == expected

    # Check whether the backend and list_blobs were actually called.
    backend.storage_client.list_blobs.assert_called_once()


def test_get_all_pages_with_no_text_files(backend, fake_client, fake_blob):

    # Setting blob's name property
    fake_blob.name = 'Example Blob.jpeg'

    # Mocking listing all the blobs of a bucket.
    fake_client.list_blobs.return_value = [fake_blob]

    # Calling the actual function with the mock data.
    result = backend.get_all_page_names()
    expected = []

    # Are we getting what we want?
    assert result == expected

    # Check whether the backend and list_blobs were actually called.
    backend.storage_client.list_blobs.assert_called_once()


def test_get_wiki_page(backend, fake_blob):

    # Mocking the download_as_string
    fake_blob.download_as_string.return_value = '{"wiki_page": "really_fake_page", "content": "really_fake_content", "date_created": "0000-00-00", "upvotes": 0, "who_upvoted": null, "downvotes": 0, "who_downvoted": null, "comments": []}'

    # Getting the dummy data
    result = backend.get_wiki_page('really_fake_page.txt')

    expected = {
        'wiki_page': 'really_fake_page',
        'content': 'really_fake_content',
        'date_created': '0000-00-00',
        'upvotes': 0,
        'who_upvoted': None,
        'downvotes': 0,
        'who_downvoted': None,
        'comments': []
    }

    assert result == expected

    # Checking the calls to the backend and fake_blob.
    backend.info_bucket.blob.assert_called_once_with('really_fake_page.txt')
    fake_blob.download_as_string.assert_called_once()


def test_get_wiki_page_failure(backend, fake_blob):

    # Patching json.loads method.
    with patch('json.loads') as mock_loads:
        # This is supposed to fail; we do not want to return anything.
        mock_loads.return_value = None

        result = backend.get_wiki_page('extremely_fake_page.txt')

        expected = None

        assert result == expected

        # Checking the calls to the backend and mock_loads.
        backend.info_bucket.blob.assert_called_once_with(
            'extremely_fake_page.txt')
        mock_loads.assert_called_once()


def test_upload(backend, fake_blob):
    # Mocking the datetime.today() with freeze_time.
    with freeze_time('1111-11-11'):
        # Mocking the upload_from_string method.
        fake_blob.upload_from_string.return_value = None

        # Mocking a file object.
        file_contents = b'fake page content'
        file = io.BytesIO(file_contents)
        file.name = 'uploaded_fake_page.txt'

        # Calling the upload method by mocking the file path
        backend.upload(file, 'uploaded_fake_page.txt')

        # Checking the calls to the backend and fake_blob
        backend.info_bucket.blob.assert_called_once_with(
            'uploaded_fake_page.txt')
        fake_blob.upload_from_string.assert_called_once_with(
            '{"wiki_page": "uploaded_fake_page.txt", "content": "fake page content", "date_created": "1111-11-11", "upvotes": 0, "who_upvoted": null, "downvotes": 0, "who_downvoted": null, "comments": []}',
            content_type='application/json')


def test_get_image(backend, fake_blob):

    #mocking the download_as_bytes
    fake_blob.download_as_bytes.return_value = b'Fake_Image_Data'

    # getting the dummy data
    result = backend.get_image('fake_image.jpeg')
    expected = base64.b64encode(b'Fake_Image_Data').decode('utf-8')
    assert result == expected

    # checking the calls to the backend and blob
    backend.info_bucket.blob.assert_called_once_with('fake_image.jpeg')
    fake_blob.download_as_bytes.assert_called_once()


def test_get_image_failure(backend, fake_blob):

    #mocking the download_as_bytes and using side_effects for exception instance
    fake_blob.download_as_bytes.side_effect = FileNotFoundError()

    #checking if value error raises or not in the backend
    with pytest.raises(ValueError) as v:
        backend.get_image('fake_not_existing_image.jpeg')
    assert str(v.value) == 'Image Name does not exist in the bucket'

    #checking the calls to the backend and blob
    backend.info_bucket.blob.assert_called_once_with(
        'fake_not_existing_image.jpeg')
    fake_blob.download_as_bytes.assert_called_once()

def test_successful_sign_up(backend, fake_blob):
    # Goal: check if we are getting a successful sign up or not
    # Goal: check if we are getting the correct account creation

    # creates fake user credentials
    fake_username = 'fake username'
    fake_password = 'fake password'
    fake_salted = f"{fake_username}{'gamma'}{fake_password}"
    fake_hashed_password = hashlib.md5(fake_salted.encode()).hexdigest()

    
    # checking username blob exits in the bucket or not
    # mocks self.user_bucket.get_blob
    # fake_blob.get_blob(fake_username).return_value = None

    # mocks getting the bucket
    with patch('google.cloud.storage.Client.bucket') as mock_bucket:
        mock_bucket.get_blob(fake_username).return_value = None

        # calling the backend sign_up
        result = backend.sign_up(fake_username, fake_password)

        # checking if the result is a User class and if the user_name matches
        assert isinstance(result, User)
        assert result.username == fake_username
        # assert blob contents is correct


def test_sign_in_user_exist(backend, fake_blob):
    # creating the fake username and password , salted , hashed passsword
    fake_username = 'fake username'
    fake_password = 'fake password'
    fake_salted = f"{fake_username}{'gamma'}{fake_password}"
    fake_hashed_password = hashlib.md5(fake_salted.encode()).hexdigest()

    # checking username blob exits in the bucket or not
    with patch('google.cloud.storage.Blob.exists') as mock_exists:
        mock_exists.return_value = True
        fake_blob.download_as_bytes.return_value = fake_hashed_password.encode(
            'utf-8')

        # calling the backend method sign_in
        result = backend.sign_in(fake_username, fake_password)

        # checking instance of User class
        assert isinstance(result, User)
        assert result.username == fake_username

    #checking the calls to the backend and blob
    backend.user_bucket.blob.assert_called_once_with(fake_username)
    mock_exists.assert_called_once()
    fake_blob.download_as_bytes.assert_called_once()


def test_sign_in_user_doesnot_exists(backend, fake_blob):
    # creating the fake username and password , salted , hashed passsword
    fake_username = 'fake username'
    fake_password = 'fake_password'
    fake_salted = f"{fake_username}{'gamma'}{fake_password}"
    fake_hashed_password = hashlib.md5(fake_salted.encode()).hexdigest()

    # checking  blob exits in the bucket or not #
    with patch('google.cloud.storage.Blob.exists') as mock_exists:
        mock_exists.return_value = False  # if blob doesnot exist

        # calling the backend method sign_in
        result = backend.sign_in(fake_username, fake_password)

        # checking the result
        assert result is None

    # checking exists was called
    mock_exists.assert_called_once()


def test_sign_in_user_incorrrect_password(backend, fake_blob):
    # creating the fake username and password , salted , hashed passsword
    fake_username = 'fake username'
    fake_password = 'fake_password'
    fake_salted = f"{fake_username}{'gamma'}{fake_password}"
    fake_hashed_password = hashlib.md5(fake_salted.encode()).hexdigest()

    # checking username blob exits in the bucket or not
    with patch('google.cloud.storage.Blob.exists') as mock_exists:
        mock_exists.return_value = True  # blob exists
        fake_blob.download_as_bytes.return_value = 'Wrong Password'.encode(
            'utf-8')  # wrong password

        # calling the backend method sign_in
        result = backend.sign_in(fake_username, fake_password)
        print('result is', result)

        # checking instance of User class
        assert result is None

    #checking the calls to the backend and blob
    backend.user_bucket.blob.assert_called_once_with(fake_username)
    mock_exists.assert_called_once()
    fake_blob.download_as_bytes.assert_called_once()


