import os.path

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    ##instnace_reletaive_config is tell the app that configuration fills are relative to folder(flask-bootstrap-gunwang) 為了要避免密碼資訊洩漏
    app = Flask(__name__, instance_relative_config=True)
    # app.instance_path   flask-bootstrap-gunwang/instance
    # set some defalut config for dev, secret key should be changed whan deploy to production
    app.config.from_mapping(
        SECRET_KEY='dev',
        # flask will not create instance folder, so u should create by youserlf
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    # == is a __eq__ magic function which can be overriden, while "is" can not be overriden
    # use is little better
    if test_config is None:
        # load the production config
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config
        app.config.from_mapping(test_config)
    try:
        os.mkdir(app.instance_path)
    except OSError:
        pass
    from . import db
    db.register_func_app(app)
    from . import auth
    app.register_blueprint(auth.bp) # register blueprints

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule("/",endpoint="index") #連接/到/index上
    @app.route("/test")
    def helloworld():
        return "helloworld"

    return app
