import os
import typing as t

from flask import Flask

def create_app(test_config=None) -> t.Any:
    """ Initialise Flask App Instance with SQLite Database 
        Returns: Flask application
    """  
    app = Flask(__name__,instance_relative_config=True)  # create and configure the app instance
    app.config.from_mapping(
        SECRET_KEY='development',
        DATABASE=os.path.join(app.instance_path,'webscrap_flask.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)   # load the instance config, if it exists, when not testing
    else:
        app.config.from_mapping(test_config)  # load the test config if passed in
    
    try: # ensure the instance folder exists
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from . import db
    db.init_app(app)

    from . import user_auth
    app.register_blueprint(user_auth.bp)

    from . import crud
    app.register_blueprint(crud.bp)
    app.add_url_rule('/', endpoint='index')

    # a simple page that says hello NOTE: to be removed
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
     
    return app
