from flask import render_template, Flask, url_for, flash, request, redirect
from flask_login import login_user, login_required, logout_user
from werkzeug.utils import secure_filename
from flaskr.backend import Backend, User
from google.cloud import storage

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
    def page(page_name):
        backend = Backend()
        file_name = page_name + '.txt'
        page_content = backend.get_wiki_page(file_name)
        return render_template('page.html', content = page_content, name = page_name)

    @app.route('/pages')
    def pages():
        backend= Backend(info_bucket_name='wiki_info')

        page_names = backend.get_all_page_names()
        return render_template('pages.html', places = page_names)

    @app.route('/about')
    def about():
        backend = Backend(info_bucket_name='wiki_info')
        author_images = {'Manish':backend.get_image('manish.jpeg'),
                        'Gabriel': backend.get_image('gabrielPic.jpg'),
                        'Myles': backend.get_image('manish.jpeg')}
        return render_template('about.html',author_images = author_images)
    
    @app.login_manager.user_loader
    def load_user(user_id):
        client = storage.Client()
        # Construct the Cloud Storage bucket name

        # Retrieve the user object from the Cloud Storage bucket
        bucket = client.bucket('wiki_login')
        blob = bucket.blob(user_id)
        user = User(blob.name)
        return user

    @app.route('/login', methods=['GET','POST'])
    def login():
        backend = Backend()

        if request.method == 'POST':
            user = backend.sign_in(request.form['username'], request.form['password'])

            if user:
                print('We are getting a user')
                login_user(user)
                return redirect('/')
            else:
                return render_template('login.html', message = 'Invalid username or password')
        
        return render_template('login.html', msg = '')
    
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect('/')
   
   
