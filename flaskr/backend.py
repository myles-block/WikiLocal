# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage

class Backend:

    def __init__(self, storage_client = storage.Client(), info_bucket_name = 'wiki_info'):
        self.storage_client = storage_client
        self.info_bucket = self.storage_client.bucket(info_bucket_name)
        
    def get_wiki_page(self, name):
        pass

    def get_all_page_names(self):
        page_names = []

        pages = self.storage_client.list_blobs(self.info_bucket)

        for page in pages:
            page_names.append(page.name)

        return page_names

    def upload(self):
        pass

    def sign_up(self):
        pass

    def sign_in(self):
        pass

    def get_image(self):
        pass

