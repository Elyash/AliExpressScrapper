"""The main app module."""

from flask_login import LoginManager

from .website import views
from .website import auth

from .interfaces import UsersMongoDBI


def create_app():
    """Create the main web app."""

    user_dbi = UsersMongoDBI()

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # TODO: refactor this.
    @login_manager.user_loader
    def load_user(email):
        return user_dbi.fetch_user(email)

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
