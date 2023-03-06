from flask import render_template ,url_for ,flash , request , redirect 
from flaskr.backend import Backend 
from werkzeug.utils import secure_filename

def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        greetings='Welcome To Our Wiki-fun in your local'
        return render_template('main.html',greetings=greetings)

    # TODO(Project 1): Implement additional routes according to the project requirements.
    

    @app.route('/pages/<page_name>')
    def show_wiki_page(page_name):
        backend = Backend()
        content_page_name = backend.get_wiki_page(page_name)
        # if content isn't found , return a 400 bad request
        return render_template('wikipage.html',name = page_name , content = content_page_name)

    @app.route('/pages')
    def pages():
        backend=Backend()
        places_page_names = backend.get_all_page_names()
        return render_template('pages.html',places_page_names= places_page_names)
    
    @app.route('/about')
    def about():
        backend=Backend()
        author_images = {'Manish':backend.get_image('manish.jpeg'),
                        'Gabriel': backend.get_image('manish.jpeg'),
                        'Myles': backend.get_image('manish.jpeg')}
        return render_template('about.html',author_images = author_images)

    ''' for uploading '''

    def allowed_file(filename):
        ''' 
        filename : first name of the file -<abc.txt-> abc
        '''
        allowed_extensions = {'txt','jpeg','jpg','png'}
        extensions = filename.split('.')[1].lower()
        if extensions in allowed_extensions:
            return True 
        else:
            return False 

    @app.route('/upload',methods=['GET','POST'])
    def upload():
        backend = Backend('wiki_info')
        if request.method == 'POST':
            if 'file' not in request.files:
                message = 'No file part'
                return render_template('upload.html',message=message)
            file = request.files['file']
            if file.filename == ' ':
                message = 'Please Select Files'
                return render_template('upload.html',message = message)
            if file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                backend.upload(file,filename)
                message = 'Uploaded Successfully'
                return render_template('upload.html',message = message)  
        return render_template('upload.html')

