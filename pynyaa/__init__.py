
from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()


def create_app(config: str) -> Flask:
    app = Flask(__name__, static_folder='assets/static')
    app.config.from_pyfile(str(config))

    db.init_app(app)
    csrf.init_app(app)

    init_blueprints(app)
    init_jinja_env(app)
    init_hooks(app)

    return app


def init_blueprints(app: Flask):
    from . import views
    app.register_blueprint(views.main)
    app.register_blueprint(views.api, url_prefix='/api/v1')

    app.errorhandler(404)(views.errors.page_not_found)


def init_jinja_env(app: Flask):
    from . import utils
    app.jinja_env.filters['pretty_size'] = utils.pretty_size
    app.jinja_env.filters['cdatasafe'] = utils.cdatasafe
    app.jinja_env.globals['url_for_other_page'] = utils.url_for_other_page


def init_hooks(app: Flask):
    from . import utils
    app.before_request(utils.inject_search_data)
