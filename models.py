from tickermain import db, login_manager, app
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    #__tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default_img.jpg')
    password = db.Column(db.String(60), nullable=False)
    #friends = db.relationship('friendsList', backref='user', lazy=True) #links the User database to the friendsList database and establishes friendsList object on User
    #mailingList = db.relationship('listMailing', backref='user', lazy=True) #links the User database to the listMailing database and establishes a collection of listMailing object on User
    #comments = db.relationship('stockChatBox', backref='user', lazy=True) #links the User database to the stockChatBox database and establishes a collection of stockChatBox object on User


class InvestmentPortfolio(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False)
    stock = db.Column(db.String(), nullable=False)
    symbol = db.Column(db.String(), nullable=False)
    original_price = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    profit_loss = db.Column(db.Integer, nullable=True)
    change = db.Column(db.Integer, nullable=True)
    original_date = db.Column(db.String(), nullable=False)
    date = db.Column(db.String(), nullable=False)


class stockChatBox(db.Model, UserMixin):
    #__tablename__ ='chat-box'
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #event listner which mirrors operations in both directions      
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False)
    stock = db.Column(db.String(), nullable=False)
    comment = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default_img.jpg')
    date = db.Column(db.String(), nullable=False)


class listMailing(db.Model):
    #__tablename__ ='mail'
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #event listner which mirrors operations in both directions   
    email = db.Column(db.String(100), primary_key=True, unique=True, nullable=False)




'''
class friendsList(db.Model):
    #__tablename__ ='friends'
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #event listner which mirrors operations in both directions   
    friends = db.Column(db.String(), nullable=False)
'''
db.create_all()
db.session.commit()

