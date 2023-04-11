'''
This module works as the backend for a Wiki Page.

Contains two classes: The User and the Backend class
which define how the application interacts with the storage system.
'''

from google.cloud import storage
from datetime import datetime
import hashlib
import base64
import hashlib
import json


class User:

    def __init__(self, username):
        '''Initializes a User object'''
        self.username = username
        self.client = storage.Client()
        self.bucket = self.client.bucket('wiki_login')
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return self.username

    def save(self, password):
        '''
        This method uploads a user information into the wiki_login bucket.
        '''
        blob = self.bucket.blob(self.username)
        salted = f"{self.username}{'gamma'}{password}"
        hashed = hashlib.md5(salted.encode())
        with blob.open("w") as f:
            f.write(hashed.hexdigest())
        return True

    def load(self):
        '''This method returns the password of the current user from the users bucket.'''
        blob = self.bucket.blob(self.username)
        data = blob.download_as_bytes()
        return data.decode('utf-8')

    @staticmethod
    def get(username):
        '''
        This method tries to find a user with the associated username in our users bucket,
        and returns a Username object with its information
        '''
        user = User(username)
        try:
            user.load()
            return User(username)
        except:
            return None


class Backend:

    def __init__(self,
                 storage_client=storage.Client(),
                 info_bucket_name='wiki_info',
                 user_bucket_name='wiki_login'):
        '''
        storage: Instantiates a client
        info_bucket_name : bucket name to store the data related to pages and about 
        '''
        self.storage_client = storage_client
        self.info_bucket = self.storage_client.bucket(info_bucket_name)
        self.user_bucket = self.storage_client.bucket(user_bucket_name)

    def get_wiki_page(self, name):  # 1

        ''' Gets an uploaded page from the content bucket
            name : name of the page files 
           '''

        # Find the wiki-page's file in the GCS bucket.
        blob = self.info_bucket.blob(name)

        # Get its content as a dictionary using the JSON API
        name_data = json.loads((blob.download_as_string()), parse_constant=None)

        # If we don't get anything, the wiki-page does not exist.
        if not name_data:
            return None

        return name_data

    def get_all_page_names(self):
        ''' Gets all the names of the pages uploaded to the wiki'''
        page_names = []

        pages = self.storage_client.list_blobs(self.info_bucket)

        for page in pages:
            extension = page.name.find('.')

            if page.name[extension:] == '.txt':
                page_names.append(page.name[:extension])

        return page_names

    def upload(self, file, filename):
        ''' Adds data to the content bucket 
         file : path of the file 
         filename : name of the file user selected
         '''
        blob = self.info_bucket.blob(filename)

        # Get today's date in YYYY-MM-DD format.
        date = datetime.today().strftime('%Y-%m-%d')

        # Set up the dictionary containing all the wiki-page's metadata.
        metadata = {
            'wiki_page': filename,
            'content': file.read().decode('utf-8'),
            'date_created': date,
            'upvotes': 0,
            'who_upvoted': None,
            'downvotes': 0,
            'who_downvoted': None,
            'comments': []
        }

        # Convert it to a JSON file.
        metadata_json = json.dumps(metadata)

        # Save it to the GCS bucket.
        blob.upload_from_string(metadata_json, content_type='application/json')


    def sign_up(self, username, password):

        ''' Adds data to the content bucket 
         user.get_id : username 
         user : user object
         '''
        salted = f"{username}{'gamma'}{password}"
        hashed = hashlib.md5(salted.encode())
        blob = self.user_bucket.blob(username)
        isExist = storage.Blob(bucket=self.user_bucket,
                               name=username).exists(self.storage_client)
        if isExist:
            return False
        else:
            with blob.open("w") as f:
                f.write(hashed.hexdigest())
            return True

    def sign_in(self, username, password):
        '''Checks if the given username and password matches a user in our GCS bucket'''
        if storage.Blob(bucket=self.user_bucket,
                        name=username).exists(self.storage_client):
            user = self.user_bucket.blob(username)

            salted = f"{username}{'gamma'}{password}"
            hashed_password = hashlib.md5(salted.encode()).hexdigest()

            pw = user.download_as_bytes()

            if hashed_password == pw.decode('utf-8'):
                return User(username)
        return None

    def get_image(self, image_name):  # 2
        '''  Returns encoded image in base64 string 
        if no image_name found , raises Value Error 
        
        Args : 
            image_name : name of the image to be get from bucket  
            
        '''

        try:
            blob = self.info_bucket.blob(image_name)
            image_data = blob.download_as_bytes()
            if image_data:
                base64_image = base64.b64encode(image_data).decode('utf-8')
                return base64_image
        except FileNotFoundError:  #handling the not existing file
            raise ValueError('Image Name does not exist in the bucket')
    
     #helper function
    def title_content(self):

        ''' return dictionary with the title name and content if exists
            else return {}

            example : {'wiki_page1': 'content'} 
        
            Args : Self
        '''
        title_content = {}
        all_pages_names = self.get_all_page_names()
        for page in all_pages_names:
            if page not in title_content:
                try:
                    page_metadata = self.get_wiki_page(page+'.txt') 
                    #checking page_metadata
                    # print('page metadata',page_metadata)
                    if page_metadata:
                        content = page_metadata.get('content')
                        title_content[page]=content
                except Exception as e:
                    pass # due to .txt json files missing in buckets
                # title_content[page]=content
        
        return title_content 

                
    def search_by_title(self, query):

        """  Returns list of pages(string) if query matched with pages 
        if query doesnot found in pages titles return empty list

        Args : 

        query : text value obtained from search form 

        """
        final_results = []
        pages_contents = self.title_content()
        for page_title in pages_contents:
            if query.lower() in page_title.lower():
                final_results.append(page_title)
        return final_results

    def search_by_content(self, query):
        """  Returns list of pages(string) if query found in content
        if query doesnot found in page-countent  returns empty list

        Args : 

        query : text value obtained from search form 

        """
        final_results = []
        pages_contents = self.title_content()
        for page_title , page_content in pages_contents.items():
            if query.lower() in page_content.lower():
                final_results.append(page_title)
        return final_results 

    def updating_metadata_with_comments(self, page_name , current_user , user_comment):

        ''' Update the wiki_page metadata with comments and user name if user makes a comment and upload to gcs 

            Args : 
                page_name : name of the wiki_page which is used to get metadata
                current_user : logged in user who makes the comment 
                comments : users comment 
        '''
        wiki_page_name = page_name + '.txt'
        page_metadata = self.get_wiki_page(wiki_page_name) #returns the page metadata in dict 

        if page_metadata:
            page_metadata['comments'].append({current_user : user_comment}) #updating the username and comments 
            updated_metadata_json = json.dumps(page_metadata)
            blob = self.info_bucket.blob(wiki_page_name)
            blob.upload_from_string(updated_metadata_json, content_type='application/json')


        
                    

        
        





        


# backend = Backend()
# print(backend.updating_metadata_with_comments('Apple Carniege Library','Manish','This place is Really Nice'))
# print(backend.get_wiki_page('Apple Carniege Library.txt'))
