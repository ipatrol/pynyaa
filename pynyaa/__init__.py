
from flask import Flask

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(config: str) -> Flask:
    app = Flask(__name__, static_folder='assets/static')
    app.config.from_pyfile(str(config))

    db.init_app(app)

    init_blueprints(app)
    init_jinja_env(app)

    return app


def init_blueprints(app: Flask):
    from . import views
    app.register_blueprint(views.main)


def init_jinja_env(app: Flask):
    from . import utils
    app.jinja_env.filters['pretty_size'] = utils.pretty_size
    app.jinja_env.filters['cdatasafe'] = utils.cdatasafe
    app.jinja_env.globals['url_for_other_page'] = utils.url_for_other_page
