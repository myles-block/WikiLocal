from flask import render_template 
from flaskr.backend import Backend 


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
    @app.route('/pages')
    def pages():
        backend= Backend(info_bucket_name='wiki_info')
        return render_template('pages.html')

    @app.route('/about')
    def about():
        backend = Backend(info_bucket_name='wiki_info')
        author_images = {'Manish':backend.get_image('manish.jpeg'),
                        'Gabriel': backend.get_image('gabrielPic.jpg'),
                        'Myles': backend.get_image('manish.jpeg')}
        return render_template('about.html',author_images = author_images)
    
    @app.route('/login')
    def login():
        return render_template('login.html')
