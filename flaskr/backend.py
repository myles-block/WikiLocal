# TODO(Project 1): Implement Backend according to the requirements.

# Imports the Google Cloud client library
from google.cloud import storage
import base64

class Backend:

    def __init__(self,bucket_name='wiki_info'):
        '''
        client :  Instantiates a client
        '''
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        
    def get_wiki_page(self, name): # 1 

        ''' Gets an uploaded page from the content bucket '''
        updated_name = name + '.txt'
        blob = self.bucket.blob(updated_name)
        name_data = blob.download_as_bytes()
        if not name_data.strip():
            return None 
        return name_data.decode('utf-8')


    def get_all_page_names(self):
        page_names = []
        blob_lists = self.client.list_blobs(self.bucket)
        print(blob_lists)
        for content in blob_lists:
            if content.name.endswith('.txt'):
                page_name = content.name.split('.')[0]
                page_names.append(page_name)
        return page_names

    def upload(self,file,filename):

        ''' Adds data to the content bucket 
         file : path of the file 
         filename : name of the file user selected
         '''
        blob = self.bucket.blob(filename)
        blob.upload_from_file(file)

    def sign_up(self):
        pass

    def sign_in(self):
        pass

    def get_image(self,image_name): # 2
        ''' Gets an image from the content bucket. '''
        blob = self.bucket.blob(image_name)
        image_data=blob.download_as_bytes()
        if image_data:
            base64_image=base64.b64encode(image_data).decode('utf-8')
            return base64_image
        else:
            return 'Error'
        
# custom=Backend('wiki_info')
# print(custom.get_all_page_names())
# print(custom.get_wiki_page('GeorgeTown Waterfront Park'))


        
    

        






