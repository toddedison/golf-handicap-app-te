import os
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, current_app, session)
from flask_login import login_user, logout_user, login_required, current_user

from .. import db
from ..models import User
from ..forms import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetForm
from ..email import send_activation_email, send_password_reset_email

auth_bp = Blueprint('auth', __name__)


# ---------------------------------------------------------------------------
# Login / Logout  (sessions_controller.rb)
# ---------------------------------------------------------------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.show', user_id=current_user.id))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            if not user.activated:
                flash('Account not activated. Check your email for the activation link.', 'warning')
                return redirect(url_for('static_pages.home'))
            login_user(user, remember=form.remember_me.data)
            next_page = session.pop('next_url', None)
            return redirect(next_page or url_for('users.show', user_id=user.id))
        flash('Invalid email/password combination', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('static_pages.home'))


# ---------------------------------------------------------------------------
# Registration  (users_controller#new + #create)
# ---------------------------------------------------------------------------
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('users.show', user_id=current_user.id))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data.lower()
        )
        user.set_password(form.password.data)
        activation_token = user.create_activation_digest()
        db.session.add(user)
        db.session.commit()
        try:
            send_activation_email(user, activation_token)
        except Exception:
            current_app.logger.warning('Could not send activation email')
        flash('Please check your email to activate your account.', 'info')
        return redirect(url_for('static_pages.home'))
    return render_template('auth/signup.html', form=form)


# ---------------------------------------------------------------------------
# Account activation  (account_activations_controller#edit)
# ---------------------------------------------------------------------------
@auth_bp.route('/activate/<token>')
def activate(token):
    email = request.args.get('email', '')
    user = User.query.filter_by(email=email).first()
    if user and not user.activated and user.authenticated('activation', token):
        user.activate()
        login_user(user)
        flash('Account activated!', 'success')
        return redirect(url_for('users.show', user_id=user.id))
    flash('Invalid activation link', 'danger')
    return redirect(url_for('static_pages.home'))


# ---------------------------------------------------------------------------
# Password reset  (password_resets_controller.rb)
# ---------------------------------------------------------------------------
@auth_bp.route('/password-reset', methods=['GET', 'POST'])
def password_reset_request():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.create_reset_digest()
            try:
                send_password_reset_email(user, token)
            except Exception:
                current_app.logger.warning('Could not send password reset email')
        flash('Email sent with password reset instructions.', 'info')
        return redirect(url_for('static_pages.home'))
    return render_template('auth/password_reset_request.html', form=form)


@auth_bp.route('/password-reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    email = request.args.get('email', '')
    user = User.query.filter_by(email=email).first()
    if not (user and user.activated and user.authenticated('reset', token)):
        return redirect(url_for('static_pages.home'))
    if user.password_reset_expired():
        flash('Password reset has expired.', 'danger')
        return redirect(url_for('auth.password_reset_request'))

    form = PasswordResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_digest = None
        db.session.commit()
        login_user(user)
        flash('Your password has been reset.', 'success')
        return redirect(url_for('users.show', user_id=user.id))
    return render_template('auth/password_reset.html', form=form, token=token, email=email)
