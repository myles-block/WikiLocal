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

    def get_wiki_page(self, name):
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
         username: username of current user
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
         username : user created username 
         password : user created password
         '''

         # Checks if blob exist with username and raise error if it does
        blob = self.user_bucket.get_blob(username)
        if blob is not None:
            raise ValueError((f"{username} already exists!"))

        # Hashes username and password with salt
        salted = f"{username}{'gamma'}{password}"
        hashed = hashlib.md5(salted.encode())


        # Creates blob with username
        blob = self.user_bucket.blob(username)

        # Get today's date in YYYY-MM-DD format.
        date = datetime.today().strftime('%Y-%m-%d')

        # Set up the dictionary containing all the author's metadata.
        metadata = {
            'hashed_password': hashed.hexdigest(),
            'account_creation': date,
            'wikis_uploaded': [],
            'wiki_history': [],
            'pfp_filename': None,
            'about_me': '',
        }

        # Convert it to a JSON file.
        metadata_json = json.dumps(metadata)

        # Save it to the GCS bucket.
        blob.upload_from_string(metadata_json, content_type='application/json')
        return User(username)

    def sign_in(self, username, password):
        '''Checks if the given username and password matches a user in our GCS bucket'''
        if storage.Blob(bucket=self.user_bucket,
                        name=username).exists(self.storage_client):
            blob = self.user_bucket.blob(username)

            # Get its content as a dictionary using the JSON API and returns none if doesn't exist
            account_data = json.loads((blob.download_as_string()),
                                      parse_constant=None)

            salted = f"{username}{'gamma'}{password}"
            hashed_password = hashlib.md5(salted.encode()).hexdigest()

            # Takes password from GCS JSON
            if hashed_password == account_data['hashed_password']:
                return User(username)
            raise ValueError(("Incorrect Password"))
        raise ValueError(("User doesn't exists!"))

    def get_image(self, image_name, bucket_name):  # 2
        ''' Gets an image from the content bucket.
            image_name : name of the image to be get from bucket
            bucket_name : denotes which bucket to use  '''

        try:
            if bucket_name == "wiki_info":
                blob = self.info_bucket.blob(image_name)
            else:
                blob = self.user_bucket.blob(image_name)
            image_data = blob.download_as_bytes()
            if image_data:
                base64_image = base64.b64encode(image_data).decode('utf-8')
                return base64_image
        except FileNotFoundError:  #handling the not existing file
            raise ValueError('Image Name does not exist in the bucket')

    def title_content(self):
        ''' return dictionary with the page name , upvote , downvote in tuple as key and it's content in value if exists
            Otherwise , returns an empty dictionary 
            example : {('wiki_page1',0,1): 'content'} 
        
            Args : Self
        '''
        title_content = {}
        page_info = self.get_all_page_names()
        for page in page_info:
            if tuple(page) not in title_content:
                try:
                    page_metadata = self.get_wiki_page(page[0] + '.txt')
                    if page_metadata:
                        content = page_metadata.get('content')
                        title_content[tuple(page)] = content
                except Exception as e:
                    continue
        return title_content

    def search_by_title(self, query):
        """  Returns list of list with page , upvotes and downvotes  if query found within the pages.
            Otherwise , return empty list
            Example : return Value -> [['page1',0,1]]

            Args : 

            query : text value obtained from search form 
        """
        final_results = []
        pages_info = self.get_all_page_names()
        for page in pages_info:
            if query.lower() in page[0].lower():
                final_results.append(page)
        return final_results

    def search_by_content(self, query):
        """  Returns list of  list with page name , upvote and downvote if query found in content
             Otherwise , returns an empty list 
             Example : query found->[['page1',0,1]] else->[]

            Args : 
            query : text value obtained from search form 

        """
        final_results = []
        pages_contents = self.title_content()
        for page, page_content in pages_contents.items():
            if query.lower() in page_content.lower():
                final_results.append(list(page))
        return final_results

    def title_date(self):
        ''' Returns dictionary with tuple containing page name , upvote and downvote as key and date_created as value
            if no any page exists , returns an empty dictionary
            Example : page_exist->[{('wikipage',0,1) : '2022-01-03'}]

            Args:
                None 
        '''
        pages_dates_created = {}
        all_page_names = self.get_all_page_names()
        for page in all_page_names:
            if tuple(page) not in pages_dates_created:
                page_metadata = self.get_wiki_page(page[0] + '.txt')
                pages_dates_created[tuple(page)] = page_metadata['date_created']
        return pages_dates_created

    def sort_pages(self, user_option):
        ''' Returns list of list with page name , upvote and downvote  by sorting them according to the user_option 
            Args : 
                user_option : option choosen by user 
                possible options : Option 1 -> A TO Z 
                                   Option 2 -> Z TO A 
                                   Option 3 -> Latest To Previous 
        '''
        page_date_created = self.title_date()
        if user_option == 'a_z':
            sorted_pages = sorted(page_date_created, key=lambda x: x[0])
        elif user_option == 'z_a':
            sorted_pages = sorted(page_date_created,
                                  key=lambda x: x[0],
                                  reverse=True)
        elif user_option == 'year':
            sorted_pages = sorted(page_date_created,
                                  key=lambda x: page_date_created[x],
                                  reverse=True)
        else:
            return []
        final_results = []
        for key in sorted_pages:
            final_results.append(list(key))
        return final_results

    def filter_by_year(self, input_date):
        ''' Returns wiki pages with the proper content,
            Ex: [[wiki_page1], [wiki_page2]]
            
            Args:
                date : date chosen by user
        '''
        page_date_created = self.title_date()
        print(page_date_created)
        final_results = []
        for wiki in page_date_created:
            date = page_date_created[wiki]
            year = datetime.strptime(date, '%Y-%m-%d').year
            if str(year) == input_date:
                final_results.append(wiki)
        return final_results

    def update_metadata_with_comments(self, page_name, current_user,
                                      user_comment):
        ''' Update the wiki_page metadata with comments and user name if user makes a comment and upload to gcs 

            Args : 
                page_name : name of the wiki_page which is used to get metadata
                current_user : logged in user who makes the comment 
                comments : users comment -> expected to receive some text since commentbox is made text required
        '''
        wiki_page_name = page_name + '.txt'
        page_metadata = self.get_wiki_page(wiki_page_name)

        if page_metadata:
            page_metadata['comments'].append({current_user: user_comment})
            updated_metadata_json = json.dumps(page_metadata)
            blob = self.info_bucket.blob(wiki_page_name)
            blob.upload_from_string(updated_metadata_json,
                                    content_type='application/json')

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

    def get_user_account(self, username):
        ''' Gets a user's account settings
            username: Current user
        '''

        # Find the user's account settings
        blob = self.user_bucket.blob(username)

        # Get its dictionary using JSON API
        account_data = json.loads((blob.download_as_string()),
                                  parse_constant=None)

        return account_data

    def update_wikiupload(self, username, fileuploaded):
        ''' Changes and overwrites account json when a user uploads a new wiki.
            username : Current user that caused action.
            fileuploaded : Filename that user uploaded
        '''
        blob = self.user_bucket.blob(username)

        # Get the current wiki_page's json file as a dictionary.
        user_metadata = Backend.get_user_account(self, username)
        user_metadata['wikis_uploaded'].append(fileuploaded)

        # Overwrite current account metadata
        blob.upload_from_string(json.dumps(user_metadata),
                                content_type='application/json')
        return user_metadata

    def update_wikihistory(self, username, file_viewed):
        ''' Changes and overwrites account json when a user views a new wiki.
            username : Current user that caused action.
            file_viewed : Filename that user viewed
        '''
        blob = self.user_bucket.blob(username)

        max_history = 100

        # Get the current wiki_page's json file as a dictionary
        user_metadata = Backend.get_user_account(self, username)

        # Checks if wiki viewed is a dupe, limit hit
        wiki_history_array = user_metadata['wiki_history']
        if file_viewed in wiki_history_array:
            index = wiki_history_array.index(file_viewed)
            wiki_history_array.pop(index)
        elif len(wiki_history_array) >= max_history:
            wiki_history_array.pop(0)

        # Adds new viewed wiki to history
        user_metadata['wiki_history'].append(file_viewed)
        # Overwrite current account metadata
        blob.upload_from_string(json.dumps(user_metadata),
                                content_type='application/json')
        return user_metadata

    def update_bio(self, username, bio):
        ''' Changes and overwrites account json when a user updates their bio.
            username : Current user that caused action.
            bio : New Bio
        '''
        blob = self.user_bucket.blob(username)

        # Get the current wiki_page's json file as a dictionary
        user_metadata = Backend.get_user_account(self, username)

        user_metadata['about_me'] = bio
        blob.upload_from_string(json.dumps(user_metadata),
                                content_type='application/json')
        return user_metadata

    def update_pfp(self, username, file):
        ''' Changes and overwrites account json when a user updates their photo.
            username : Current user that caused action.
            file : Profile Photo file
        '''
        user_blob = self.user_bucket.blob(username)

        # Creates Photoname
        photo_name = username + ".jpg"

        # Checks if a photo already exists and deletes old photo
        isExist = storage.Blob(bucket=self.user_bucket,
                               name=photo_name).exists(self.storage_client)
        if isExist:
            existBlob = self.user_bucket.blob(photo_name)
            generation_match_precondition = None
            existBlob.reload()
            existBlob.delete(if_generation_match=generation_match_precondition)

        # Uploads photo to GCS
        photo_blob = self.user_bucket.blob(photo_name)
        generation_match_precondition = 0
        photo_blob.upload_from_file(
            file, if_generation_match=generation_match_precondition)
        # Get the current wiki_page's json file as a dictionary
        user_metadata = Backend.get_user_account(self, username)

        # Add photo to GCS
        user_metadata['pfp_filename'] = photo_name
        user_blob.upload_from_string(json.dumps(user_metadata),
                                     content_type='application/json')
        return user_metadata
