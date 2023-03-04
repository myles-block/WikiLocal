from flaskr.backend import Backend
from unittest.mock import MagicMock
import pytest 
import base64 

# TODO(Project 1): Write tests for Backend methods.
@pytest.fixture
def fake_blob():
    ''' mocking the blob object as it is one of the dependency on the backend class'''
    return MagicMock()

@pytest.fixture
def bucket(fake_blob):
    bucket = MagicMock()
    bucket.blob.return_value = fake_blob # returns the value of fake_blob
    return bucket 

@pytest.fixture 
def backend(bucket):
    backend = Backend(info_bucket_name='test_bucket')
    backend.info_bucket = bucket 
    return backend 

def test_get_image(backend, fake_blob):

    #mocking the download_as_string
    fake_blob.download_as_bytes.return_value = b'Fake_Image_Data'
    # getting the dummy data 
    result = backend.get_image('fake_image.jpeg')
    expected = base64.b64encode(b'Fake_Image_Data').decode('utf-8')
    assert result == expected 
    # checking the calls to the backend and blob 
    backend.info_bucket.blob.assert_called_once_with('fake_image.jpeg')
    fake_blob.download_as_bytes.assert_called_once()




