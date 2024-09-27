"""The main app page backend."""

import json
import requests

from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user

from Utils import models
from WebApp import app

views = Blueprint('views', __name__)


### Continue here! get just the link and enter it to rabbit MQ.
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    """Home page to add new gift, show all gifts and remove them."""

    if request.method == 'POST':
        link = request.form.get('gift_link')

        if requests.get(link, timeout=300).status_code != 200:
            flash(f'Invalid gift link. Check it avaliable (link: {link})', category='error')
            return render_template("home.html", user=current_user)

        gift_request = models.GiftRequest(link=link, email=current_user.email)
        app.gift_requests_publisher_rabbitmqi.publish_gift_request(gift_request)

        flash('Gift added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-gift', methods=['POST'])
def delete_gift():
    """Removes a gift."""

    gift = json.loads(request.data.get('')) # this function expects a JSON from the INDEX.js file 
    gift_name = gift['gift_name']

    fetched_gift = app.gifts_dbi.fetch_gift(gift_name)
    if fetched_gift and fetched_gift.email == current_user.email:
        app.gifts_dbi.remove_gift(gift_name)

    return jsonify({})
