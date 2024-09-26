"""The main app page backend."""

import json
import requests

from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user

from ..models import Gift


views = Blueprint('views', __name__)


### Continue here! get just the link and enter it to rabbit MQ.
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        name = request.form.get('gift_name')
        link = request.form.get('gift_link')
        description = request.form.get('gift_description')
        images = request.form.get('gift_images')
        price = request.form.get('gift_price')
        email = request.form.get('email')

        if len(name) < 2:
            flash(f'Invalid gift name. Should be longer then {len(name)} chars', category='error')
            return render_template("home.html", user=current_user)
        
        if image:
            try:
                status = requests.get(image, timeout=2000).status_code
            except requests.exceptions.RequestException as e:
                flash(f'Invalid image link. Details: {e.args}', category='error')
                return render_template("home.html", user=current_user)
            if status != 200:
                flash(f'Gift link is unreachable, status code: {status}', category='error')
            return render_template("home.html", user=current_user)
        
        if not price:
            price = -1
        try:
            price = float(price)
        except ValueError as e:
            flash(f'Invalid price. Details: {e.args}', category='error')
            return render_template("home.html", user=current_user)

        new_gift = Gift(
            name=name, image=image, price=price, description=description, user_id=current_user.id
        )  #providing the schema for the gift 
        db.session.add(new_gift) #adding the gift to the database
        db.session.commit()
        flash('Gift added!', category='success')    

        print(db.session.query(Gift).all())
    return render_template("home.html", user=current_user)


@views.route('/delete-gift', methods=['POST'])
def delete_gift():  
    gift = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    giftId = gift['giftId']
    gift = Gift.query.get(giftId)
    if gift:
        if gift.user_id == current_user.id:
            db.session.delete(gift)
            db.session.commit()

    return jsonify({})
