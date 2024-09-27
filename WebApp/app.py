"""The main app module.
It opens web page with login and sign-up options ->
It stores the sign-up data in Users collection in MongoDB ->
It sends the home page (upon sucessfull login) ->
It fetches the user's gifts from MongoDB's Gift collection ->
It shows the gifts ->
It enable to add and remove gifts, as follow:
    Add:
        -> publish a gift_request to gift_requests_queue
        -> consumes this gift_request from scrapped_gifts_queue
        -> fetches the gift data from mongoDB's Gifts collection
    Remove:
        -> Delete the gift from mongoDB Gifts collection
"""

import flask
import flask_login

from WebApp.website import views, auth

from Utils.interfaces import UsersMongoDBI, GiftsMongoDBI, GiftRequestsPubliserRabbitMQI


users_dbi = UsersMongoDBI()
gifts_dbi = GiftsMongoDBI()
gift_requests_publisher = GiftRequestsPubliserRabbitMQI()
# TODO: implement: scrapped_gifts_consumer = GiftRequestsConsumerRabbitMQI()

app = flask.Flask(__name__)

def create_app():
    """Create the main web app."""

    app.secret_key = 'super secret key'

    app.register_blueprint(views.views, url_prefix='/')
    app.register_blueprint(auth.auth, url_prefix='/')

    login_manager = flask_login.LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # This is a strange way but this is how flask_login works..
    @login_manager.user_loader
    def load_user(email: str):
        return users_dbi.fetch_user(email)

    return app


if __name__ == '__main__':
    create_app()

    app.run(debug=True, host='0.0.0.0')
