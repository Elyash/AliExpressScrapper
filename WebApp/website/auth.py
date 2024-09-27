"""Authentication module for the web app."""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user

from werkzeug.security import generate_password_hash, check_password_hash

from Utils import models, interfaces


auth = Blueprint('auth', __name__)

USERS_DBI = interfaces.UsersMongoDBI()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """A login to user account."""

    if request.method != 'POST':
        return render_template("login.html", user=current_user)

    email = request.form.get('email')
    password = request.form.get('password')

    fetched_user = USERS_DBI.fetch_user(email)

    if fetched_user:
        if check_password_hash(password, fetched_user.password):
            flash('Logged in successfully!', category='success')
            login_user(fetched_user, remember=True)
            return redirect(url_for('views.home'))
        else:
            flash('Incorrect password, try again.', category='error')
    else:
        flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    """Logout from the user."""

    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    """Sign up for a new user."""

    if request.method != 'POST':
        return render_template("sign_up.html", user=current_user)

    if len(request.form.get('email')) < 4:
        flash('Email must be greater than 3 characters.', category='error')
    elif len(request.form.get('first_name')) < 2:
        flash('First name must be greater than 1 character.', category='error')
    elif request.form.get('password1') != request.form.get('password2'):
        flash('Passwords don\'t match.', category='error')
    elif len(request.form.get('password1')) < 7:
        flash('Password must be at least 7 characters.', category='error')
    else:
        new_user = models.User(
            email=request.form.get('email'),
            first_name = request.form.get('first_name'),
            password = generate_password_hash(
                request.form.get('password1'),
                method='pbkdf2:sha256'
            )
        )
        if USERS_DBI.fetch_user(new_user.email):
            flash('Email already exists.', category='error')
        else:
            USERS_DBI.store_user(new_user)
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)
