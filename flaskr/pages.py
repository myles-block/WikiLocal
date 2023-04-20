from flask import render_template, Flask, url_for, flash, request, redirect
from flask_login import login_user, login_required, logout_user
from flaskr.backend import Backend, User
from werkzeug.utils import secure_filename
from google.cloud import storage


def make_endpoints(app,backend):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        greetings = 'Welcome To Our Wiki-fun in your local'
        return render_template('main.html', greetings=greetings)

    # TODO(Project 1): Implement additional routes according to the project requirements.

    @app.route('/pages/<page_name>')
    def page(page_name):
        '''This route handles displaying the content of any wiki page within our wiki_info GCS bucket'''

        file_name = page_name + '.txt'
        page_content = backend.get_wiki_page(file_name)
        return render_template('page.html',
                               content=page_content,
                               name=page_name)

    @app.route('/pages')
    def pages():

        page_names = backend.get_all_page_names()
        return render_template('pages.html', places=page_names)

    @app.route('/about')
    def about():
   
        author_images = {
            'Manish': backend.get_image('manish.jpeg'),
            'Gabriel': backend.get_image('gabrielPic.jpg'),
            'Myles': backend.get_image('mylesPic.jpg')
        }
        return render_template('about.html', author_images=author_images)

    @app.login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        '''
        This route attempts to log a user with a POST request. 
        Otherwise, it just renders a login form where users can try to log in with their credentials
        '''


        if request.method == 'POST':
            user = backend.sign_in(request.form['username'],
                                   request.form['password'])

            if user:
                login_user(user)
                return redirect('/')
            else:
                return render_template('login.html',
                                       message='Invalid username or password')

        return render_template('login.html', msg='')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        msg = ''
        if request.method == 'POST':
            completed = backend.sign_up(request.form['username'],
                                        request.form['password'])
            if completed:
                user = backend.sign_in(request.form['username'],
                                       request.form['password'])
                login_user(user)
                return redirect('/')
            else:
                msg = "This username already exists! Pick a new one!"
                return render_template('signup.html', message=msg)
        return render_template('signup.html')

    @app.route("/logout")
    @login_required
    def logout():
        '''This route logs out the current user'''

        logout_user()
        return redirect('/')

    @app.route('/upload', methods=['GET', 'POST'])
    def upload():

        if request.method == 'POST':
            print(request.files)
            if 'file' not in request.files:
                message = 'No file part'
                return render_template('upload.html', message=message)
            file = request.files['file']
            if file.filename == ' ':
                message = 'Please Select Files'
                return render_template('upload.html', message=message)
            if file.filename and allowed_file(file.filename):
                # filename = secure_filename(file.filename)
                backend.upload(file,
                               request.form['wikiname'] + ".txt")  #workaround
                message = 'Uploaded Successfully'
                return render_template('upload.html', message=message)
        return render_template('upload.html')

    def allowed_file(filename):
        ''' 
        filename : first name of the file -<abc.txt-> abc
        '''
        allowed_extensions = {'txt', 'jpeg', 'jpg', 'png'}
        extensions = filename.split('.')[1].lower()
        if extensions in allowed_extensions:
            return True
        else:
            return False
    
    @app.route('/search',methods = ["GET","POST"])
    def search():
        '''  post the resulted pages from the user query in pages.html

        '''
        if request.method == "POST":
            search_query = request.form.get('search_query')
            search_by = request.form.get('search_by')
            if search_by == 'title':
                resulted_pages = backend.search_by_title(search_query)
                if len(resulted_pages) > 0:
                    return render_template('pages.html',places = resulted_pages)
                else:
                    message = f"No such pages found for '{search_query}' " 
                    return render_template('pages.html',message = message )
            elif search_by == 'content':
                resulted_pages = backend.search_by_content(search_query)
                if len(resulted_pages) > 0:
                    return render_template('pages.html',places = resulted_pages)
                else:
                    message = f"No such pages found with '{search_query}' in the content "
                    return render_template('pages.html',message = message )              
        else:
            return redirect('/pages.html',200)
    
    @app.route('/sort', methods =["GET" ,"POST"])
    def sort():
        ''' post the resulted pages from user option of sorting 
            if resulted pages exist otherise redirect pages 

        '''
        if request.method == "POST":
            user_option = request.form.get("sort_option")
            required_pages = backend.sort_pages(user_option)
    
            return render_template('pages.html' , places = required_pages , sort_order=user_option)

        return redirect('/pages.html')

    @app.route('/sortyears', methods =["GET" ,"POST"])
    def sort_by_year():
        if request.method == "POST":
            user_option = request.form.get("list_years")
            required_pages = backend.filter_by_year(str(user_option))
            return render_template('pages.html' , places = required_pages , sort_order=user_option)

        return redirect('/pages.html')






    
