# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
from flask_login import login_manager
import hashlib
import base64


class User:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.is_authenticated = False
    
    def get_id(self):
        return self.username


class Backend:

    def __init__(self, storage_client = storage.Client(), info_bucket_name = 'wiki_info', user_bucket_name = 'wiki_login'):
        self.storage_client = storage_client
        self.info_bucket = self.storage_client.bucket(info_bucket_name)
        self.user_bucket = self.storage_client.bucket(user_bucket_name)
    
    def get_wiki_page(self, name): # 1 
        ''' Gets an uploaded page from the content bucket '''
        blob = self.info_bucket.blob(name)
        name_data = blob.download_as_bytes()
        if not name_data.strip():
            return None 
        return name_data.decode('utf-8')

    def get_all_page_names(self):
        ''' Gets all the names of the pages uploaded to the wiki'''
        page_names = []

        pages = self.storage_client.list_blobs(self.info_bucket)

        for page in pages:
            extension = page.name.find('.')

            if page.name[extension:] == '.txt':
                page_names.append(page.name[:extension])

        return page_names

    def upload(self):
        pass

    def sign_up(self):
        pass

    def sign_in(self, username, password):
        if storage.Blob(bucket= self.user_bucket, name=username).exists(self.storage_client):
            user = self.user_bucket.blob(username)
            
            salted = f"{username}{'gamma'}{password}"
            hashed_password = hashlib.blake2b(salted.encode()).hexdigest()

            pw = user.download_as_bytes()

            if hashed_password == pw.decode('utf-8'):
                return User(username, pw)
        return None

    def get_image(self,image_name): # 2

        ''' Gets an image from the content bucket. '''

        blob = self.info_bucket.blob(image_name)
        image_data=blob.download_as_bytes()
        if image_data:
            base64_image=base64.b64encode(image_data).decode('utf-8')
        return base64_image
        
# custom=Backend('wiki_info')
# print(custom.get_image('manish.jpeg'))
        
    

        






