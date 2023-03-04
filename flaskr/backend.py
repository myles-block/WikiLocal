# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import base64

class User:

    def __init__(self, username, password, pages_created = []):
        self.username = username
        self.password = password
        self.pages_created = pages_created
        self.is_authenticated = False
    
    def get_id(self):
        return self.username
    
class Backend:

    def __init__(self, storage_client = storage.Client(), info_bucket_name = 'wiki_info'):
        self.storage_client = storage_client
        self.info_bucket = self.storage_client.bucket(info_bucket_name)
        
    def get_wiki_page(self, name): # 1 
        ''' Gets an uploaded page from the content bucket '''
        blob = self.info_bucket.blob(name)
        name_data = blob.download_as_bytes()
        if not name_data.strip():
            return None 
        return name_data.decode('utf-8')

    def get_all_page_names(self):
        page_names = []

        pages = self.storage_client.list_blobs(self.info_bucket)

        for page in pages:
            extension = page.name.find('.')

            page_names.append(page.name[:extension])

        return page_names

    def upload(self):
        pass

    def sign_up(self):
        pass

    def sign_in(self):
        pass

    def get_image(self,image_name): # 2

        ''' Gets an image from the content bucket. '''

        blob = self.info_bucket.blob(image_name)
        image_data=blob.download_as_bytes()
        if image_data:
            base64_image=base64.b64encode(image_data).decode('utf-8')
        return base64_image
        
# custom=Backend('wiki_info')
# print(custom.get_image('manish.jpeg'))
        
    

        






