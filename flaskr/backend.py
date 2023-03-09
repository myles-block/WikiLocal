# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
from flask_login import login_manager
import hashlib
import base64
import hashlib


class User:

    def __init__(self, username):
        self.username = username
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    
    def get_id(self):
        return self.username

class Backend:

    def __init__(self, storage_client = storage.Client(), info_bucket_name = 'wiki_info', user_bucket_name = 'wiki_login'):
        '''
        storage: Instantiates a client
        info_bucket_name : bucket name to store the data related to pages and about 
        '''
        self.storage_client = storage_client
        self.info_bucket = self.storage_client.bucket(info_bucket_name)
        self.user_bucket = self.storage_client.bucket(user_bucket_name)
        
    def get_wiki_page(self, name): # 1 

        ''' Gets an uploaded page from the content bucket
            name : name of the page files 
           '''
        
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
        ''' Adds data to the content bucket 
         file : path of the file 
         filename : name of the file user selected
         '''
        blob = self.info_bucket.blob(filename)
        blob.upload_from_file(file)

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

    def sign_in(self, username, password):
        '''Checks if the given username and password matches a user in our GCS bucket'''
        if storage.Blob(bucket= self.user_bucket, name=username).exists(self.storage_client):
            user = self.user_bucket.blob(username)
            
            salted = f"{username}{'gamma'}{password}"
            hashed_password = hashlib.md5(salted.encode()).hexdigest()

            pw = user.download_as_bytes()
                        
            if hashed_password == pw.decode('utf-8'):
                return User(username)
        return None

    def get_image(self,image_name): # 2

        ''' Gets an image from the content bucket.
            image_name : name of the image to be get from bucket  '''

        try: 
            blob = self.info_bucket.blob(image_name)
            image_data=blob.download_as_bytes()
            if image_data:
                base64_image=base64.b64encode(image_data).decode('utf-8')
                return base64_image
        except FileNotFoundError : #handling the not existing file
            raise ValueError('Image Name does not exist in the bucket')
        







