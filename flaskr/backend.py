# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import base64
import hashlib

class User:

    def __init__(self, username, password, pages_created = []):
        self.username = username
        self.password = password
        self.pages_created = pages_created
        self.is_authenticated = False
    
    def get_id(self):
        return self.username
    
class Backend:

    def __init__(self, storage_client = storage.Client(), info_bucket_name = 'wiki_info', user_bucket_name = 'wiki_login'):
        '''
        storage: Instantiates a client
        info_bucket_name : bucket nanme to store the data related to pages and about '''

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

    def upload(self,file,filename):
        pass

    def sign_up(self, username, password):
        ''' Adds data to the content bucket 
         user.get_id : username 
         user : user object
         '''
        # return user object & redirect home 
        salted = f"{username}{'gamma'}{password}"
        hashed = hashlib.md5(salted.encode())
        blob = self.user_bucket.blob(username)
        isExist = storage.Blob(bucket= self.user_bucket, name=username).exists(self.storage_client)
        if isExist: # if exist
            return False # unsuccessful
        else:
            with blob.open("w") as f:
                f.write(hashed.hexdigest())
            return True # successful
        #return postive sign up, or negative sign up

    def sign_in(self):
        pass

    def get_image(self,image_name): # 2

        ''' Gets an image from the content bucket. '''

        try: 
            blob = self.info_bucket.blob(image_name)
            image_data=blob.download_as_bytes()
            if image_data:
                base64_image=base64.b64encode(image_data).decode('utf-8')
                return base64_image
        except FileNotFoundError : #handling the not existing file
            raise ValueError('Image Name doesnot exist in the bucket')
        

        
    

        






