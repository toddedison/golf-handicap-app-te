from flask import render_template, current_app
from flask_mail import Message
from . import mail


def send_activation_email(user, token):
    msg = Message(
        subject='Golf Handicapper – Activate Your Account',
        recipients=[user.email]
    )
    msg.html = render_template('email/activation.html', user=user, token=token)
    msg.body = render_template('email/activation.txt', user=user, token=token)
    mail.send(msg)


def send_password_reset_email(user, token):
    msg = Message(
        subject='Golf Handicapper – Password Reset',
        recipients=[user.email]
    )
    msg.html = render_template('email/password_reset.html', user=user, token=token)
    msg.body = render_template('email/password_reset.txt', user=user, token=token)
    mail.send(msg)
