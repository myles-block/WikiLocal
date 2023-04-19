from flaskr.backend import Backend, User
from unittest.mock import MagicMock, patch
import unittest
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
    bucket.get_blob.return_value = None
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


def test_get_image_upload(backend, fake_blob):

    #mocking the download_as_bytes
    fake_blob.download_as_bytes.return_value = b'Fake_Image_Data'

    # getting the dummy data
    result = backend.get_image('fake_image.jpeg', "wiki_info")
    expected = base64.b64encode(b'Fake_Image_Data').decode('utf-8')
    assert result == expected

    # checking the calls to the backend and blob
    backend.info_bucket.blob.assert_called_once_with('fake_image.jpeg')
    fake_blob.download_as_bytes.assert_called_once()


def test_get_image_account(backend, fake_blob):
    #mocking the download_as_bytes
    fake_blob.download_as_bytes.return_value = b'Fake_Image_Data'

    # getting the dummy data
    result = backend.get_image('fake_image.jpeg', "wiki_login")
    expected = base64.b64encode(b'Fake_Image_Data').decode('utf-8')
    assert result == expected

    # checking the calls to the backend and blob
    backend.user_bucket.blob.assert_called_once_with('fake_image.jpeg')
    fake_blob.download_as_bytes.assert_called_once()


def test_get_image_failure_upload(backend, fake_blob):

    #mocking the download_as_bytes and using side_effects for exception instance
    fake_blob.download_as_bytes.side_effect = FileNotFoundError()

    #checking if value error raises or not in the backend
    with pytest.raises(ValueError) as v:
        backend.get_image('fake_not_existing_image.jpeg', "wiki_login")
    assert str(v.value) == 'Image Name does not exist in the bucket'

    #checking the calls to the backend and blob
    backend.user_bucket.blob.assert_called_once_with(
        'fake_not_existing_image.jpeg')
    fake_blob.download_as_bytes.assert_called_once()


def test_get_image_failure_account(backend, fake_blob):

    #mocking the download_as_bytes and using side_effects for exception instance
    fake_blob.download_as_bytes.side_effect = FileNotFoundError()

    #checking if value error raises or not in the backend
    with pytest.raises(ValueError) as v:
        backend.get_image('fake_not_existing_image.jpeg', "wiki_info")
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

    with freeze_time('1111-11-11'):
        with patch('hashlib.md5') as mock_hashlib:
            # calling the backend sign_up
            mock_hashlib.return_value.hexdigest.return_value = "fake"
            result = backend.sign_up(fake_username, fake_password)

            # don't need to patch, because we imported json library
            fake_blob.upload_from_string.assert_called_once_with(
                '{"hashed_password": "fake", "account_creation": "1111-11-11", "wikis_uploaded": [], "wiki_history": [], "pfp_filename": null, "about_me": ""}',
                content_type='application/json')

            # make sure we are calling the fake_blob
            backend.user_bucket.blob.assert_called_once()

            # make sure we are calling the fake_blob with the approiate username
            backend.user_bucket.blob.assert_called_once_with(fake_username)

            #checks if user is returned
            assert isinstance(result, User)
            assert result.username == fake_username


def test_failed_sign_up(backend, fake_blob):
    # creates fakes credentials
    fake_username = 'fake username'
    fake_password = 'fake password'

    # sets .get_blob to return "something" instead of None
    backend.user_bucket.get_blob.return_value = "something"
    result = backend.sign_up(fake_username, fake_password)

    # checks that it is None and asserts the calls
    assert result == None
    backend.user_bucket.get_blob.assert_called_once()
    backend.user_bucket.get_blob.assert_called_once_with(fake_username)


def test_sign_in_user_exist(backend, fake_blob):
    # creating the fake username and password , salted , hashed passsword
    fake_username = 'fake username'
    fake_password = 'fake password'
    fake_salted = f"{fake_username}{'gamma'}{fake_password}"
    fake_hashed_password = hashlib.md5(fake_salted.encode()).hexdigest()

    # checking username blob exits in the bucket or not
    with patch('google.cloud.storage.Blob.exists') as mock_exists:
        # mocks hashlib
        with patch('hashlib.md5') as mock_hashlib:
            # sets download as string to our return value
            fake_blob.download_as_string.return_value = (
                '{"hashed_password": "fake", "account_creation": "1111-11-11", "wikis_uploaded": [], "wiki_history": [], "pfp_filename": null, "about_me": ""}'
            )
            # sets haslib password to fix
            mock_hashlib.return_value.hexdigest.return_value = "fake"

            # forces the return value of the if to be true
            mock_exists.return_value = True

            # calling the backend method sign_in
            result = backend.sign_in(fake_username, fake_password)

            # checking instance of User class
            assert isinstance(result, User)
            assert result.username == fake_username

    #checking the calls to the backend and blob
    backend.user_bucket.blob.assert_called_once_with(fake_username)
    mock_exists.assert_called_once()
    fake_blob.download_as_string.assert_called_once()


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
        fake_blob.download_as_string.return_value = (
            '{"hashed_password": "incorrect_password", "account_creation": "1111-11-11", "wikis_uploaded": [], "wiki_history": [], "pfp_filename": null, "about_me": ""}'
        )

        # calling the backend method sign_in
        result = backend.sign_in(fake_username, fake_password)
        print('result is', result)

        # checking instance of User class
        assert result is None

    #checking the calls to the backend and blob
    backend.user_bucket.blob.assert_called_once_with(fake_username)
    mock_exists.assert_called_once()
    fake_blob.download_as_string.assert_called_once()


def test_get_user_account_success(backend, fake_blob):
    # fake username
    fake_username = 'fake username'

    # mock download as string return value
    fake_blob.download_as_string.return_value = (
        '{"hashed_password": "fake", "account_creation": "1111-11-11", "wikis_uploaded": [], "wiki_history": [], "pfp_filename": null, "about_me": ""}'
    )

    # call backend function with username
    result = backend.get_user_account(fake_username)

    #expected result
    expected_dict = {
        "hashed_password": "fake",
        "account_creation": "1111-11-11",
        "wikis_uploaded": [],
        "wiki_history": [],
        "pfp_filename": None,
        "about_me": ""
    }

    assert isinstance(result, dict)
    assert result == expected_dict
    backend.user_bucket.blob.assert_called_with(fake_username)
    fake_blob.download_as_string.assert_called_once()


def test_user_get_account_failure(backend, fake_blob):
    # fake username
    fake_username = 'fake username'

    # set the return value to none
    with patch("json.loads") as mock_loader:
        mock_loader.return_value = None

        # call backend
        result = backend.get_user_account(fake_username)

        # assert that result is none and blob is called
        assert result is None
        backend.user_bucket.blob.assert_called_with(fake_username)
        mock_loader.assert_called_once()


def test_update_wikihistory_add_one(backend, fake_blob):
    fake_username = 'fake username'
    file_viewed = 'filename'

    # creates return value from get_user_account method
    getter = {
        "hashed_password": "fake",
        "account_creation": "1111-11-11",
        "wikis_uploaded": [],
        "wiki_history": [],
        "pfp_filename": None,
        "about_me": ""
    }

    # injects return value into get_user_account
    with patch.object(Backend, 'get_user_account',
                      return_value=getter) as mock_method:
        # expected dictionary of what it should be when you view a wiki
        expected_dict = {
            "hashed_password": "fake",
            "account_creation": "1111-11-11",
            "wikis_uploaded": [],
            "wiki_history": ["filename"],
            "pfp_filename": None,
            "about_me": ""
        }
        # calls to backend
        result = backend.update_wikihistory(fake_username, file_viewed)

        # checks if result matches and is of type dictionary
        assert isinstance(result, dict)
        assert result == expected_dict

        # checks that blob is called
        backend.user_bucket.blob.assert_called_with(fake_username)
        mock_method.assert_called_once()
        fake_blob.upload_from_string.assert_called_once()
        fake_blob.upload_from_string.assert_called_once_with(
            json.dumps(expected_dict), content_type='application/json')


def test_update_wikihistory_autoadjust(backend, fake_blob):
    fake_username = 'fake username'
    file_viewed = 'filename11'

    # creates return value from get_user_account method
    getter = {
        "hashed_password": "fake",
        "account_creation": "1111-11-11",
        "wikis_uploaded": [],
        "wiki_history": [
            "filename", "filename2", "filename3", "filename4", "filename5",
            "filename6", "filename7", "filename8", "filename9", "filename 10"
        ],
        "pfp_filename": None,
        "about_me": ""
    }

    # injects return value into get_user_account
    with patch.object(Backend, 'get_user_account',
                      return_value=getter) as mock_method:
        # expected dictionary of what it should be when you view a wiki
        expected_dict = {
            "hashed_password": "fake",
            "account_creation": "1111-11-11",
            "wikis_uploaded": [],
            "wiki_history": [
                "filename2", "filename3", "filename4", "filename5", "filename6",
                "filename7", "filename8", "filename9", "filename 10",
                "filename11"
            ],
            "pfp_filename": None,
            "about_me": ""
        }
        # calls to backend
        result = backend.update_wikihistory(fake_username, file_viewed)

        # checks if result matches and is of type dictionary
        assert isinstance(result, dict)
        assert result == expected_dict

        # checks that blob is called
        backend.user_bucket.blob.assert_called_with(fake_username)
        mock_method.assert_called_once()
        fake_blob.upload_from_string.assert_called_once()
        fake_blob.upload_from_string.assert_called_once_with(
            json.dumps(expected_dict), content_type='application/json')


def test_update_wikihistory_same_view(backend, fake_blob):
    fake_username = 'fake username'
    file_viewed = 'filename2'

    # creates return value from get_user_account method
    getter = {
        "hashed_password": "fake",
        "account_creation": "1111-11-11",
        "wikis_uploaded": [],
        "wiki_history": ["filename1", "filename2", "filename3"],
        "pfp_filename": None,
        "about_me": ""
    }

    # injects return value into get_user_account
    with patch.object(Backend, 'get_user_account',
                      return_value=getter) as mock_method:
        # expected dictionary of what it should be when you view a wiki
        expected_dict = {
            "hashed_password": "fake",
            "account_creation": "1111-11-11",
            "wikis_uploaded": [],
            "wiki_history": ["filename1", "filename3", "filename2"],
            "pfp_filename": None,
            "about_me": ""
        }
        # calls to backend
        result = backend.update_wikihistory(fake_username, file_viewed)

        # checks if result matches and is of type dictionary
        assert isinstance(result, dict)
        assert result == expected_dict

        # checks that blob is called
        backend.user_bucket.blob.assert_called_with(fake_username)
        mock_method.assert_called_once()
        fake_blob.upload_from_string.assert_called_once()
        fake_blob.upload_from_string.assert_called_once_with(
            json.dumps(expected_dict), content_type='application/json')


def test_update_wikiupload(backend, fake_blob):
    fake_username = 'fake username'
    file_uploaded = 'filename'

    # creates return value from get_user_account method
    getter = {
        "hashed_password": "fake",
        "account_creation": "1111-11-11",
        "wikis_uploaded": [],
        "wiki_history": [],
        "pfp_filename": None,
        "about_me": ""
    }

    with patch.object(Backend, 'get_user_account',
                      return_value=getter) as mock_method:
        # expected dictionary of what it should be when you view a wiki
        expected_dict = {
            "hashed_password": "fake",
            "account_creation": "1111-11-11",
            "wikis_uploaded": ["filename"],
            "wiki_history": [],
            "pfp_filename": None,
            "about_me": ""
        }

        # calls to backend
        result = backend.update_wikiupload(fake_username, file_uploaded)

        # checks if result matches and is of type dictionary
        assert isinstance(result, dict)
        assert result == expected_dict

        # asserts
        backend.user_bucket.blob.assert_called_with(fake_username)
        mock_method.assert_called_once()
        fake_blob.upload_from_string.assert_called_once()
        fake_blob.upload_from_string.assert_called_once_with(
            json.dumps(expected_dict), content_type='application/json')


def test_update_bio(backend, fake_blob):
    fake_username = 'fake username'

    getter = {
        "hashed_password": "fake",
        "account_creation": "1111-11-11",
        "wikis_uploaded": [],
        "wiki_history": [],
        "pfp_filename": None,
        "about_me": ""
    }

    with patch.object(Backend, 'get_user_account',
                      return_value=getter) as mock_method:
        # expected dictionary of what it should be when you view a wiki
        expected_dict = {
            "hashed_password": "fake",
            "account_creation": "1111-11-11",
            "wikis_uploaded": [],
            "wiki_history": [],
            "pfp_filename": None,
            "about_me": "This is my fake bio"
        }
        bio = "This is my fake bio"
        result = backend.update_bio(fake_username, bio)

        # assert that the blob exists
        backend.user_bucket.blob.assert_called_with(fake_username)

        # checks if result matches and is of type dictionary
        assert isinstance(result, dict)
        assert result == expected_dict

        # further assertions
        mock_method.assert_called_once()
        fake_blob.upload_from_string.assert_called_once()
        fake_blob.upload_from_string.assert_called_once_with(
            json.dumps(expected_dict), content_type='application/json')


# how am I checking the photo contents in the end
def test_update_pfp_no_existence(backend, fake_blob):
    fake_username = "fake username"
    photo_name = fake_username + ".jpg"
    file = b'Fake_Image_Data'

    getter = {
        "hashed_password": "fake",
        "account_creation": "1111-11-11",
        "wikis_uploaded": [],
        "wiki_history": [],
        "pfp_filename": None,
        "about_me": ""
    }

    # checking user photo blob exits in the bucket or not
    with patch('google.cloud.storage.Blob.exists') as mock_exists:
        mock_exists.return_value = False
        with patch.object(Backend, 'get_user_account',
                          return_value=getter) as mock_method:
            # expected dictionary of what it should be when you view a wiki
            expected_dict = {
                "hashed_password": "fake",
                "account_creation": "1111-11-11",
                "wikis_uploaded": [],
                "wiki_history": [],
                "pfp_filename": photo_name,
                "about_me": ""
            }
            # fake_blob.upload_from_file.return_value = file
            result = backend.update_pfp(fake_username, file)

            # checks if result matches and is of type dictionary
            assert isinstance(result, dict)
            assert result == expected_dict

            # assert that the blob is called from buckets
            backend.user_bucket.blob.assert_called_with(photo_name)

            # assert that your get_accounts is being called
            mock_method.assert_called_once()

            # checks that upload from file is getting called with parameters
            fake_blob.upload_from_file.assert_called_once()
            fake_blob.upload_from_file.assert_called_once_with(
                b'Fake_Image_Data', if_generation_match=0)

            # checks if upload from string is getting called with parameters
            fake_blob.upload_from_string.assert_called_once()
            fake_blob.upload_from_string.assert_called_once_with(
                json.dumps(expected_dict), content_type='application/json')


def test_update_pfp_with_existence(backend, fake_blob):
    fake_username = "fake username"
    photo_name = fake_username + ".jpg"
    file = b'Fake_Image_Data'

    getter = {
        "hashed_password": "fake",
        "account_creation": "1111-11-11",
        "wikis_uploaded": [],
        "wiki_history": [],
        "pfp_filename": "we_exist_alr_bro!!",
        "about_me": ""
    }

    # checking user photo blob exits in the bucket or not
    with patch('google.cloud.storage.Blob.exists') as mock_exists:
        mock_exists.return_value = True
        with patch.object(Backend, 'get_user_account',
                          return_value=getter) as mock_method:
            # expected dictionary of what it should be when you view a wiki
            expected_dict = {
                "hashed_password": "fake",
                "account_creation": "1111-11-11",
                "wikis_uploaded": [],
                "wiki_history": [],
                "pfp_filename": photo_name,
                "about_me": ""
            }

            # fake_blob.upload_from_file.return_value = file
            result = backend.update_pfp(fake_username, file)

            # assert that the blob is called from buckets
            backend.user_bucket.blob.assert_called_with(photo_name)

            # checks if result matches and is of type dictionary
            assert isinstance(result, dict)
            assert result == expected_dict

            # assert that your get_accounts is being called
            mock_method.assert_called_once()

            # checks that upload from file is getting called with parameters
            fake_blob.upload_from_file.assert_called_once()
            fake_blob.upload_from_file.assert_called_once_with(
                b'Fake_Image_Data', if_generation_match=0)

            # checks if upload from string is getting called with parameters
            fake_blob.upload_from_string.assert_called_once()
            fake_blob.upload_from_string.assert_called_once_with(
                json.dumps(expected_dict), content_type='application/json')