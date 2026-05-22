from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, FloatField, IntegerField, SubmitField
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                NumberRange, Optional, ValidationError)
from .models import User


class LoginForm(FlaskForm):
    email       = StringField('Email',    validators=[DataRequired(), Email()])
    password    = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit      = SubmitField('Log in')


class SignupForm(FlaskForm):
    name                  = StringField('Name',     validators=[DataRequired(), Length(max=50)])
    email                 = StringField('Email',    validators=[DataRequired(), Email(), Length(max=255)])
    password              = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password_confirmation = PasswordField('Password confirmation',
                            validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Create my account')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')


class EditProfileForm(FlaskForm):
    name                  = StringField('Name',  validators=[DataRequired(), Length(max=50)])
    email                 = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    password              = PasswordField('Password', validators=[Optional(), Length(min=8)])
    password_confirmation = PasswordField('Password confirmation',
                            validators=[EqualTo('password', message='Passwords must match')])
    picture = FileField('Add a profile picture',
                        validators=[Optional(), FileAllowed(['jpg','jpeg','gif','png'], 'Images only.')])
    submit  = SubmitField('Save changes')


class PasswordResetRequestForm(FlaskForm):
    email  = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send reset email')


class PasswordResetForm(FlaskForm):
    password              = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password_confirmation = PasswordField('Password confirmation',
                            validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Reset password')


class RoundForm(FlaskForm):
    course    = StringField('Course', validators=[DataRequired(), Length(max=40)],
                            render_kw={'placeholder': 'Augusta National'})
    game_date = StringField('Date',   validators=[DataRequired(), Length(max=40)],
                            render_kw={'placeholder': 'mm/dd/yyyy', 'data-behavior': 'datepicker'})
    slope     = FloatField('Slope',   validators=[DataRequired(), NumberRange(min=55, max=155)],
                           render_kw={'placeholder': 'e.g. 55–155', 'min': '55', 'max': '155'})
    rating    = FloatField('Rating',  validators=[DataRequired(), NumberRange(min=50, max=78)],
                           render_kw={'placeholder': 'e.g. 60–78', 'step': '0.1'})
    score     = IntegerField('Score', validators=[DataRequired(), NumberRange(min=59, max=130)],
                             render_kw={'placeholder': 'e.g. 100', 'min': '59', 'max': '130'})
    submit    = SubmitField('Save round')
