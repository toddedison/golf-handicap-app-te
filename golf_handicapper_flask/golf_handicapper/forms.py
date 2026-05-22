from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional, ValidationError

from .models import User


# ---------------------------------------------------------------------------
# Auth forms
# ---------------------------------------------------------------------------
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password_confirmation = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    submit = SubmitField('Sign Up')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')


class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField('New Password', validators=[Optional(), Length(min=8)])
    password_confirmation = PasswordField(
        'Confirm Password',
        validators=[EqualTo('password', message='Passwords must match')]
    )
    picture = FileField('Profile Picture', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only.')
    ])
    submit = SubmitField('Save Changes')


# ---------------------------------------------------------------------------
# Password reset forms
# ---------------------------------------------------------------------------
class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Email')


class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    password_confirmation = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    submit = SubmitField('Reset Password')


# ---------------------------------------------------------------------------
# Round form  (was micropost)
# ---------------------------------------------------------------------------
class RoundForm(FlaskForm):
    course = StringField('Course Name', validators=[DataRequired(), Length(max=40)])
    game_date = StringField('Date Played', validators=[DataRequired(), Length(max=40)])
    slope = FloatField('Slope Rating', validators=[
        DataRequired(),
        NumberRange(min=55, max=155, message='Slope must be between 55 and 155')
    ])
    rating = FloatField('Course Rating', validators=[
        DataRequired(),
        NumberRange(min=60, max=80, message='Rating must be between 60 and 80')
    ])
    score = IntegerField('Gross Score', validators=[
        DataRequired(),
        NumberRange(min=55, max=200, message='Score must be between 55 and 200')
    ])
    submit = SubmitField('Save Round')
