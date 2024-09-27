"""The main app module."""

from flask_login import LoginManager

from .website import views
from .website import auth

from ..Utils.interfaces import UsersMongoDBI, GiftsMongoDBI, GiftRequestsPubliserRabbitMQI


users_dbi = UsersMongoDBI()
gifts_dbi = GiftsMongoDBI()
gift_requests_publisher_rabbitmqi = GiftRequestsPubliserRabbitMQI()


def create_app():
    """Create the main web app."""

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # TODO: refactor this.
    @login_manager.user_loader
    def load_user(email):
        return users_dbi.fetch_user(email)

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
