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
    '''
    Simulates the authentication credentials of a user within a login system.

    It possesses methods to search for any existing user in our database, and if found, retrieve its
    login information.

    Attributes:
        username = The name, as a str, of the user as it was entered when they signed up.
        client = An instance of a google cloud storage client.
        bucket = An instance of the user information GCS bucket storing all our users profile information. 
        is_authenticated = States, through a boolean, if the current user has provided valid credentials.
        is_active = States, through a boolean, if the current user is the one holding a session and interacting with the client.
        is_anonymous = States, through a boolean, if the current user's profile information is unknown.
    '''

    def __init__(self, username):
        '''Initializes a User object'''
        self.username = username
        self.client = storage.Client()
        self.bucket = self.client.bucket('wiki_login')
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def load(self):
        '''This method checks if a username matches an existing user in our user-information GCS bucket.
            If successful, it returns the password of the current user from the users bucket.'''
        blob = self.bucket.blob(self.username)
        data = blob.download_as_bytes()
        return data.decode('utf-8')

    def get_id(self):
        '''
        This method works along the login_user method from login_manager to retrieve the authenticated user's username.
        '''
        return self.username

    @staticmethod
    def get(username):
        '''
        This method tries to find a user with the associated username in our users bucket,
        and returns a Username object with its information.
        username: The backend will check if there is a profile under the name of this username.
        '''
        user = User(username)
        try:
            user.load()
            return User(username)
        except:
            return None


class Backend:
    '''
    As the name implies, serves the functionality of the backend section of a project, communicating the database with user's interaction.

    It possesses methods to retrieve, create, delete, and update content from the google cloud storage database.
    As it handles the HTTP requests dealing with google cloud storage, it is also responsible of handling data type conversion,
    reading, and writing from GCS buckets blobs.

    Attributes:
        storage_client = An instance of a google cloud storage client.
        info_bucket_name = Specifies the name of the GCS bucket containing the wiki project's wiki page text files.
        user_bucket_name = Specifies the name of teh GCS bucket containing the login credentials of the wiki project users.
    '''

    def __init__(self,
                 storage_client=storage.Client(),
                 info_bucket_name='wiki_info',
                 user_bucket_name='wiki_login'):
        '''
        Constructor for the Backend class. It provides its attributes with default values
        for mock injection purposes
        '''
        self.storage_client = storage_client
        self.info_bucket = self.storage_client.bucket(info_bucket_name)
        self.user_bucket = self.storage_client.bucket(user_bucket_name)

    def get_wiki_page(self, name):  # 1
        ''' Gets an uploaded page's metadata information from the content bucket as a dictionary.
            name : Name of the wiki page to be found and retrieved.
           '''
        blob = self.info_bucket.blob(name)
        name_data = json.loads((blob.download_as_string()), parse_constant=None)

        # If we don't get anything, the wiki-page does not exist.
        if not name_data:
            return None

        return name_data

    def get_all_page_names(self):
        ''' Gets all the names and the rating of the pages uploaded to the wiki'''

        # To 'display' the name of every wiki page, we will construct a list containing every wiki page's metadata stored in the backend.
        page_names = []

        pages = self.storage_client.list_blobs(self.info_bucket)

        for page in pages:
            # For each page, we will populate a dictionary containing each wiki page's information.
            page_information = []
            extension = page.name.find('.')

            # We only want to retrieve information related to wiki page files, not any other type of file.
            if page.name.endswith('.txt'):
                page_metadata = Backend.get_wiki_page(self, page.name)
                page_information.append(page.name[:extension])
                page_information.append(page_metadata['upvotes'])
                page_information.append(page_metadata['downvotes'])
                page_names.append(page_information)

        return page_names

    def upload(self, file, filename):
        ''' Adds data to the content bucket 
         file : path of the file 
         filename : name of the file user selected
         '''
        blob = self.info_bucket.blob(filename)

        date = datetime.today().strftime('%Y-%m-%d')

        # Set up a dictionary containing all the wiki-page's metadata, which will then be converted to a JSON file to be stored.
        metadata = {
            'wiki_page': filename,
            'content': file.read().decode('utf-8'),
            'date_created': date,
            'upvotes': 0,
            'who_upvoted': [],
            'downvotes': 0,
            'who_downvoted': [],
            'comments': []
        }
        metadata_json = json.dumps(metadata)
        blob.upload_from_string(metadata_json, content_type='application/json')

    def sign_up(self, username, password):
        ''' Adds data to the content bucket 
         user.get_id : username 
         user : User object
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
        ''' Gets an image from the content bucket.
            image_name : name of the image to be get from bucket  '''

        try:
            blob = self.info_bucket.blob(image_name)
            image_data = blob.download_as_bytes()
            if image_data:
                base64_image = base64.b64encode(image_data).decode('utf-8')
                return base64_image
        except FileNotFoundError:  #handling the not existing file
            raise ValueError('Image Name does not exist in the bucket')

    def update_page(self, action_taken, username, page_name):
        ''' Updates a wiki-page's json file in terms of
            its vote count and comments section.
            action_taken : The user action that triggered this method. E.g. Upvoted, downvoted,or posted a comment.
            username : The name of the user that took the action.
            page_name : The name of the wiki page that will be changed.  
        '''
        blob = self.info_bucket.blob(page_name)

        # Get the current wiki_page's json file as a dictionary.
        page_metadata = Backend.get_wiki_page(self, page_name)

        # If the user just upvoted this page, update the page's vote count in the dictionary.
        if action_taken == 'upvote':
            # If the user has already upvoted for this page, then remove his vote from the page's vote count.
            if username in page_metadata['who_upvoted']:
                page_metadata['upvotes'] -= 1
                page_metadata['who_upvoted'].remove(username)

            # Every user can only have one vote at a time for any wiki page.
            elif username in page_metadata['who_downvoted']:
                page_metadata['downvotes'] -= 1
                page_metadata['who_downvoted'].remove(username)

            # If it's the user's first time voting for this page, then simply add its
            # vote to the upvote count of the wiki page.
            else:
                page_metadata['upvotes'] += 1
                page_metadata['who_upvoted'].append(username)

        # Do the same for when the user downvotes the  wiki page.
        elif action_taken == 'downvote':
            if username in page_metadata['who_downvoted']:
                page_metadata['downvotes'] -= 1
                page_metadata['who_downvoted'].remove(username)

            elif username in page_metadata['who_upvoted']:
                page_metadata['upvotes'] -= 1
                page_metadata['who_upvoted'].remove(username)

            else:
                page_metadata['downvotes'] += 1
                page_metadata['who_downvoted'].append(username)

        # Once we have changed our wiki page's metadata, overwrite its json file with the updated version.
        blob.upload_from_string(json.dumps(page_metadata),
                                content_type='application/json')

        # Returning the updated dictionary for testing purposes.
        return page_metadata
