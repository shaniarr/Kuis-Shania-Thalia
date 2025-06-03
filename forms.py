from random import choice
from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, FileField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    medical_number = IntegerField('Medical Number', validators=[DataRequired()])
    submit = SubmitField('Register')
    hospital = SelectMultipleField(u'Hospital', choices=[('rsui', 'Rumah Sakit Universitas Indonesia'), ('rspui', 'Rumah Sakit Puri Indah'), ('rspoi', 'Rumah Sakit Pondok Indah')])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ResetPassword(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    new_password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired()])
    submit = SubmitField('Reset Password')
