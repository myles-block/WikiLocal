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

    ''' mocking the bucket injecting fake_blob '''

    bucket = MagicMock()
    bucket.blob.return_value = fake_blob # returns the value of fake_blob
    return bucket 

@pytest.fixture 
def backend(bucket):
    backend = Backend('test_bucket')
    backend.bucket = bucket 
    return backend 

def test_get_image(backend, fake_blob):

    #mocking the download_as_bytes
    fake_blob.download_as_bytes.return_value = b'Fake_Image_Data'

    # getting the dummy data 
    result = backend.get_image('fake_image.jpeg')
    expected = base64.b64encode(b'Fake_Image_Data').decode('utf-8')
    assert result == expected 

    # checking the calls to the backend and blob 
    backend.bucket.blob.assert_called_once_with('fake_image.jpeg')
    fake_blob.download_as_bytes.assert_called_once()

def test_get_image_failure(backend,fake_blob):

    #mocking the download_as_bytes and using side_effects for exception instance
    fake_blob.download_as_bytes.side_effect = FileNotFoundError()

    #checking if value error raises or not in the backend
    with pytest.raises(ValueError) as v:
        backend.get_image('fake_not_existing_image.jpeg')
    assert str(v.value) == 'Image Name doesnot exist in the bucket'
   
    #checking the calls to the backend and blob
    backend.bucket.blob.assert_called_once_with('fake_not_existing_image.jpeg')
    fake_blob.download_as_bytes.assert_called_once()

    

    