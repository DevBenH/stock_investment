from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from tickermain.models import User

#These forms use object orientated programming which makes there object easier to access and manipulate in the routes.py file
#Create a form the user uses for searching for a specific stock
class searchStockForm(FlaskForm):
    #DataRequired() - this data must be entered for the form to be valid
    search = StringField('Search', validators = [DataRequired()])
    submit = SubmitField("Search")

#This form allows the user to enter account details when registering an account
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    #EqualTo() - the form is only valid if the password is equal to the appropriate password in the database
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign Up")

    #Subroutine used to check account credentials - username
    def validate_username(self, username):
        #Select all existing usernames from the database where the username is the same as the inputed username
        user = User.query.filter_by(username = username.data).first()
        #If there is the same username in the database - the username has been taken
        if user:
            #Error handling - if the username already exists - alert the user
            raise ValidationError('This username is taken. Please choose a different one')
    
    #Subroutine used to check account credentials - email
    def validate_email(self, email):
        #Select all existing emails from the database where the email is the same as the inputed email
        email = User.query.filter_by(email = email.data).first()
        #If there is the same email in the database - the email has been taken
        if email:
            #Error handling - if the email already exists - alert the user
            raise ValidationError('This email is taken. Please choose a different one')

#Form used for logging into a specific account
class LoginForm(FlaskForm):
    #Username has minimum and maximum length restraints
    #DataRequired() means these values have to be inputed for the form to be valid
    username = StringField('Username', validators = [DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    #Checkbox form item - set to true if checked and false if left unchecked
    remember = BooleanField('Remember Me')
    submit = SubmitField("Login")

#Form used to update account credentials on the account page
class UpdateForm(FlaskForm):
    #Username has minimum and maximum length restraints
    #DataRequired() means these values have to be inputed for the form to be valid
    username = StringField('Username', validators = [DataRequired(), Length(min=3, max=20)])
    #The Email() function means that this has to be inputed in the form of an email
    email = StringField('Email', validators = [DataRequired(), Email()])
    picture = FileField('Update Profile picture', validators=[FileAllowed(['png', 'jpg'])])
    submit = SubmitField("Update")

    #Subroutine used to check account credentials - username
    def validate_username(self, username):
        if username.data != current_user.username:
            #Select all existing usernames from the database where the username is the same as the inputed username
            user = User.query.filter_by(username = username.data).first()
            #If there is the same username in the database - the username has been taken
            if user:
                #Error handling
                raise ValidationError('This username is taken. Please choose a different one')
    
    #Subroutine used to check account credentials - email
    def check_email(self, email):
        if email.data != current_user.email:
            #Select all existing emails from the database where the email is the same as the inputed email
            email = User.query.filter_by(email = email.data).first()
            #If there is the same email in the database - the email has been taken
            if email:
                #If the email already exists - alert the user
                raise ValidationError('This email is taken. Please choose a different one')

#Form used in the modal where the user invests into their chosen stocks
class InvestForm(FlaskForm):
    stock = StringField('Stock Symbol', validators = [DataRequired(), Length(min=1, max=50)])
    price = IntegerField('Price at Purchase')
    submit = SubmitField("Add Stock")

#Form for posting comments in the specifc chat boxes for the stocks
class chatUploadForm(FlaskForm):
    comment = StringField('Comment', validators = [DataRequired(), Length(min=2, max=100)])
    upload = SubmitField("Send Message")

#Button that downloads a file containing the users investment portfolio
class downloadForm(FlaskForm):
        download = SubmitField("Download")

#Form used for signing up to the newsletter which is sent out every Wednesday
class newsletterForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    #Button used to POST requests to the site
    submit = SubmitField("Sign Up")
