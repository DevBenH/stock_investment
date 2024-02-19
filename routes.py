#Imports relevant subroutines and modules
from flask import render_template, url_for, flash, redirect, request, send_from_directory, abort 
from pandas_datareader import data as pdr 
from pandas_datareader._utils import RemoteDataError
import pandas as pd 
import matplotlib.pyplot as plt 
import matplotlib
import numpy as np 
import datetime 
from datetime import datetime, timedelta 
import base64 
import yfinance as yf 
import re 
import os, ssl
from bs4 import BeautifulSoup as soup 
#from urllib.request import urlopen 
#import cherrypy
from sqlalchemy.sql import func 
from sklearn.tree import DecisionTreeRegressor 
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import math 
from tickermain.forms import RegistrationForm, LoginForm, UpdateForm, InvestForm, chatUploadForm, downloadForm, newsletterForm, searchStockForm
from tickermain.models import User, InvestmentPortfolio, stockChatBox, listMailing
from tickermain import app, db, bcrypt, mail
from flask_login import login_user, logout_user, current_user, login_required
import secrets 
from PIL import Image
import random
import time 
from flask_mail import Message 
import smtplib 
import calendar 
from .graph import updateGraph, predictGraph
from .pmcc import calculatePmcc
from .check_day import check_if_new_day, check_if_new_week
from .investment_flag import buyOrSell, investmentStage
from .investment_algorithm import find_recommended_stocks
from .save_pictures import save_picture
from .merge import splitMerge, sortMerge


#Prevents cache error
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)): 
    ssl._create_default_https_context = ssl._create_unverified_context 

matplotlib.use('Agg')

#Account details used for sending emails
EMAIL_ADDRESS = 'hben18711@gmail.com'
EMAIL_PASSWORD = 'fjlrjhtaoxegomxs' 


#Updates the page cache so it can refresh the images
@app.after_request   
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

#Initialises the landing page
@app.route('/') 
@app.route('/landing') 
def landingPage():
    return render_template('landing.html', title='Welcome') 

#Initialises the home page
@app.route('/home', methods=['POST', 'GET']) 
@login_required
def home(): 
    #Timer used to measure loading times
    start = time.perf_counter() 
    #Connects variables to forms
    form1 = InvestForm() 
    form2 = chatUploadForm()
    form3 = newsletterForm()
    form4 = searchStockForm()

    search = ''
    #Checks if there has been a request to push data through the form
    if request.method == "POST":
        try:
            #Gets the search input data
            search = request.form['search']
            #Opens file
            file = open("tickermain/tickerlist.txt", "r")
            for line in file:
                #Converts company name to ticker symbol by using the tickerlist.txt file
                if search in line.split(',')[2]:
                    company_name = line.split(',')[0]

            #If no company name found in file
            if company_name == '':
                #Alert the user with a warning message
                #flash(f'No results found for: { search }!', 'Danger')
                #Set default URL to Amazon search
                url = "https://www.bbc.co.uk/search?q=Amazon" + "+shares"
                company_name='AMZN'
                search = 'Amazon'
                #Refresh the page by redirecting the user back to the home page
                return redirect('home')

            #If company name found, add it to the URL which will be webscraped
            else:
                url = "https://www.bbc.co.uk/search?q=" + search + "+shares"

            #Close the file
            file.close()

        #If there is an error in the company name (issues arise with fullstops within name)
        except ValueError:
            #Set URL as default URL
            url = "https://www.bbc.co.uk/search?q=Amazon" + "+shares"
            company_name='AMZN'
        
        #Pass in company name and ticker symbol to the graph functions
        #updateGraph(search, company_name)
        #predictGraph(search, company_name)
    #Otherwise initialise default graphs
    
    else:
        url = "https://www.bbc.co.uk/search?q=Amazon" + "+shares"
        company_name='AMZN'
        search = 'Amazon'
        #updateGraph('Amazon', 'AMZN')
        #predictGraph('Amazon', 'AMZN')
    
    #Webscraping initialisation
    uClient = urlopen(url)
    #Read the pages HTML corresponding to the URL created
    raw_html = uClient.read()
    #Close the client which reads the HTML once the code has been fetched
    uClient.close()
    #Store the HTML code in a variable 
    main_html = soup(raw_html, 'html.parser') 
    #Filter through the HTML code to find required data about newsfeed
    #Finding the images HTML
    containers = main_html.findAll("div", {"class": "ssrcss-jusods-PromoImageContainerInner ehnfhlg1"})
    images = main_html.findAll("img")
    len_containers = len(containers)
    #Finding the header and paragraph HTML
    containers = main_html.findAll("div", {"class": "ssrcss-l100ew-PromoContentSummary e1f5wbog1"})
    #Creating the stock data
    #Set time restraints for the data 
    end_date = str(datetime.now().strftime('%Y-%m-%d'))
    start_date = str((datetime.now()-timedelta(days=31)).strftime('%Y-%m-%d'))   
    #Using the time restraints, get the stock data for the specifc company name which has been searched 
    data = pdr.get_data_yahoo(company_name, start=start_date, end=end_date)
    #Gets the adjacent cloe data
    y = data['Adj Close']
    #Calculates product moment correlation cofficient value and assigns it to the variable pmcc
    pmcc = calculatePmcc(y)
    #If positive correlation assign green colour to text
    if pmcc >= 0:
        color_change_pmcc = '#4CAC69'
    #Otherwise, if negative correlation, assign red colour to text
    else:
        color_change_pmcc = '#DE3639'
    
    #Set new time restraints for other stock data
    end_date = str(datetime.now().strftime('%Y-%m-%d'))
    start_date = str((datetime.now()-timedelta(days=3)).strftime('%Y-%m-%d'))   
    #Fetch the other stock data
    df = pdr.get_data_yahoo(company_name, start=start_date, end=end_date)
    #Assign each stock data to a variable and round to three decimal places
    high = round(df['High'][0],3)
    low = round(df['Low'][0],3)
    open_value = round(df['Open'][0],3)
    close = round(df['Close'][0],3)
    volume = round(df['Volume'][0],3)
    adj_close = round(df['Adj Close'][1],3)

    #Create new time restraints to fetch yesteray adjacent close value used for calculating the percentage difference each day 
    end_date = str(datetime.now().strftime('%Y-%m-%d'))
    start_date = str((datetime.now()-timedelta(days=3)).strftime('%Y-%m-%d'))   
    df = pdr.get_data_yahoo(company_name, start=start_date, end=end_date)

    #Round value to three decimal places
    yesterday_adj_close = round(df['Adj Close'][0],3)
    #Use yesterdays value and today value to calculate a percentage difference
    difference = adj_close - yesterday_adj_close
    percentage_difference = round((((difference)/yesterday_adj_close)*100),3)
    difference = round(difference, 3)

    #If there is a positive difference (stock price has increased since yesterday) assign green colour to text
    if difference >= 0:
        color_change_difference = '#4CAC69'
        positive_difference = True
    #If there is a negative difference (stock price has decreased since yesterday) assign red colour to text
    else:
        color_change_difference = '#DE3639'
        positive_difference = False
    
    #This section is used for updating the users investments so that they change according to the stock market 
    #Check if it is a new day
    if check_if_new_day() == True:
        #Get todays date
        date_today = str(datetime.now().strftime('%Y-%m-%d'))
        #Select all of the users investements that are not already updated (have a different date than today)
        user_info = InvestmentPortfolio.query.filter(InvestmentPortfolio.date != date_today).all()
        #Loop through thee selected investments 
        for i in range(len(user_info)):
            #Update these investments so that they have the current date which shows they have been updated 
            #Updates the database
            user_info[i].date == str(datetime.now().strftime('%Y-%m-%d'))
            #Create new time restraints 
            end_date = str(datetime.now().strftime('%Y-%m-%d'))
            start_date = str((datetime.now()-timedelta(days=3)).strftime('%Y-%m-%d'))   
            #Update the old stock data and change the money the user has invested to its refreshed amount 
            df = pdr.get_data_yahoo(user_info[i].symbol, start=start_date, end=end_date)
            update_adj_close = round(df['Adj Close'][0],5)
            end_date = datetime.strptime(user_info[i].original_date, '%Y-%m-%d')
            start_date = str((end_date-timedelta(days=2)).strftime('%Y-%m-%d'))
            df = pdr.get_data_yahoo(user_info[i].symbol, start=start_date, end=end_date)
            update_yesterday_adj_close = round(df['Adj Close'][0],5)
            update_percentage_difference = round((((update_adj_close - update_yesterday_adj_close)/update_yesterday_adj_close)*100),4)
            user_info[i].change = update_percentage_difference
            #Calculate how much profit or loss the user has made since yesterday
            user_info[i].profit_loss = round(((user_info[i].change/100) * user_info[i].original_price), 3)
            user_info[i].price = round((((user_info[i].change / 100) * user_info[i].price) + user_info[i].original_price),3)
            #Commit these changes to the database
            db.session.commit()

    #Uses investment stratedy to create a but or sell graph
    #Fetches adjacent close data for specific time restraints 
    end_date = str(datetime.now().strftime('%Y-%m-%d'))
    start_date = str((datetime.now()-timedelta(days=1000)).strftime('%Y-%m-%d'))

    data = pdr.get_data_yahoo(company_name, start=start_date, end=end_date)

    Ticker = pd.DataFrame()
    Ticker['Adj Close'] = data['Adj Close']

    #Gets the short rolling average and long rolling average
    shortA = pd.DataFrame()
    #Short average has a window of 10 days
    shortA['Adj Close'] = data['Adj Close'].rolling(window=10).mean()

    longA = pd.DataFrame()
    #Long avarage ha a window of 100 days
    longA['Adj Close'] = data['Adj Close'].rolling(window=100).mean()

    data = pd.DataFrame()
    data['Ticker'] = Ticker['Adj Close']
    data['shortA'] = shortA['Adj Close']
    data['longA'] = longA['Adj Close']

    #Get data from buy or sell subroutine 
    buy_sell = buyOrSell(data)

    data['activateBuy'] = buy_sell[0]
    data['activateSell'] = buy_sell[1]
    #Create buy or sell graph
    plt.figure(figsize=(16, 8))
    plt.style.use('fivethirtyeight')
    plt.plot(data['Ticker'], label = company_name, alpha=0.4)
    plt.plot(data['shortA'], label = 'Short Average', alpha=0.4)
    plt.plot(data['longA'], label = 'Long Average', alpha=0.4)

    plt.plot(data.index, data['activateBuy'], label='Buy', marker='^', markersize=10, color='green')
    plt.plot(data.index, data['activateSell'], label='Sell', marker='v', markersize=10, color='red')
    plt.title('Buy or Sell')
    #Save the graph to the system and name it buyorsell.png
    plt.savefig('/Users/benjaminhardy/Ticker/tickermain/static/images/buyorsell.png') 


    #If the investment form has been submitted and the current user is logged in and has permissions 
    if form1.validate_on_submit() and current_user.is_authenticated:
        investment_date = str(datetime.now().strftime('%Y-%m-%d'))
        #Open file 
        file_name = open("tickermain/tickerlist.txt", "r")
        for line in file_name:
            if form1.stock.data in line.split(',')[2]:
                company_ticker = line.split(',')[0]
        #Add a new row to the InvestmentPortfolio databse and add the desired stock and price that the user has entered in the form
        user_portfolio = InvestmentPortfolio(username=current_user.username, stock=form1.stock.data, symbol=company_ticker, original_price=form1.price.data,  price=form1.price.data, profit_loss=0, change=0, original_date=investment_date, date=investment_date)
        #Add this module
        db.session.add(user_portfolio)
        #Commit these changes to the database
        db.session.commit()

    #If the chat upload form has been submitted and the user is logged in and has permissions
    if form2.validate_on_submit() and current_user.is_authenticated:
        upload_date = str(datetime.now().strftime('%Y-%m-%d'))
        #Upload the message submitted from the form to the database
        upload_message = stockChatBox(username=current_user.username, stock=search, comment=form2.comment.data, image_file=current_user.image_file, date=upload_date)
        #Add module to the database 
        db.session.add(upload_message)
        #Commit the changes to the database
        db.session.commit()
        #Refresh the page so that it shows the latest chat messages
        return redirect(url_for('home'))

    #If the newsletter form has been submitted and the current user is logged in and has permissions
    if form3.validate_on_submit() and current_user.is_authenticated:
        #Add their email to the database and commit the changes so the database updates
        new_email = listMailing(email=form3.email.data)
        db.session.add(new_email)
        db.session.commit()

    #Get all the messages the current user has sent to the specific chat box on the specific stock they are looking at 
    user_messages = stockChatBox.query.filter_by(stock=search, username=current_user.username).all()
    len_user_messages = len(user_messages)

    #Loop through these messages and divide them into ones the user has sent and ones other users has sent
    #This is so they messages the user has sent appear on the left and messages other users have sent appear on the right
    for i in range(len(user_messages)):
        if current_user.username != user_messages[i].username:
            user_messages[i].username = current_user.username

        if current_user.image_file != user_messages[i].image_file:
            user_messages[i].image_file = current_user.image_file

    other_messages = stockChatBox.query.filter(stockChatBox.username != current_user.username).filter(stockChatBox.stock==search).all()
    main_messages = stockChatBox.query.filter_by(stock=search).all()

    len_main_messages = len(main_messages)
    len_user_messages = len(user_messages)
    len_other_messages = len(other_messages)

    #Initilaises the users profile picture or assign them a default profile picture if they havent added one manually
    if current_user.is_authenticated:
        profile_picture = url_for('static', filename='profilepicture/' + current_user.image_file)
    else:
        profile_picture = 'default_img.jpg'
    
    #Stop the loading time counter once the operations have been completed (the page has loaded) and assign it to a variable 
    finish = time.perf_counter()
    #print(f'Finished in {round(finish-start, 2)} second(s)')

    #Pass all of the variable to the home.html file (pass variables from backend to front end)
    #I assign a variable to each values that they can be referred to as in the HTML 
    return render_template('home.html', 
    form1=form1,
    form2=form2,
    form3=form3,
    form4=form4,
    containers=containers, 
    len_containers=len_containers, 
    images=images, 
    high=high, 
    low=low, 
    open_value=open_value, 
    close=close, 
    volume=volume, 
    adj_close=adj_close, 
    search=search, 
    company_name=company_name, 
    yesterday_adj_close=yesterday_adj_close, 
    difference=difference, 
    percentage_difference=percentage_difference, 
    pmcc=pmcc, 
    color_change_pmcc=color_change_pmcc, 
    color_change_difference=color_change_difference,
    profile_picture = profile_picture,
    positive_difference=positive_difference,
    user_messages=user_messages,
    len_user_messages=len_user_messages,
    other_messages=other_messages,
    len_other_messages=len_other_messages,
    main_messages=main_messages,
    len_main_messages=len_main_messages,)


#Creates the connection from the front end to the backend for the investment page
@app.route('/invest', methods=['GET', 'POST']) #Accepts post and get requests made by the user 
@login_required
def invest():
    #Assigns variables to the form data
    form1 = InvestForm()
    form3 = downloadForm()

    #Starts the timer - used for measuring the page loading times
    start = time.perf_counter()

    #Gets all of the investment data made by the uer currently logged in 
    #This data includes stocks that they have invested in and how much they have invested in them
    user_info = InvestmentPortfolio.query.filter_by(username=current_user.username).all()
    #Gets the length (how many companys they are invested in)
    len_user_info = len(user_info)

    #If the current user that is logged in and has permissions
    if current_user.is_authenticated:
        #If they have their own profile picture, initialise it
        profile_picture = url_for('static', filename='profilepicture/' + current_user.image_file)
    else:
        #Otherwise, set them the default profile picture
        profile_picture = 'default_img.jpg'

    #If the user has made a request to download a file containing all of their investments to their computer
    if form3.validate_on_submit():
        if form3.download.data == True:
            #Download the file
            return redirect(url_for('download'))

    #sorting the percentage changes with a merge sort
    investmentPrices = InvestmentPortfolio.query.filter_by(username=current_user.username).all()
    #Create an empty array
    prices_to_sort = []
    #Loop through each percentage change for each stock and append them to an empty array
    #A merge sort is going to be performed on this array which will find the least percentage change and the most percentage change for all of the users investments
    for i in range(len(investmentPrices)):
        prices_to_sort.append(investmentPrices[i].change)

    #Perform the merge sort on this data using the subroutine in the merge.py file
    #This merge sort uses recurssion
    sorted_percentage_change = splitMerge(prices_to_sort)
    len_sorted_percentage_change = len(sorted_percentage_change)


    #Aggregate SQL functions
    #This is used to provide the user with useful analytics about their investments
    #This find the sum of all the users investments 
    sumPrice = db.session.query(func.sum(InvestmentPortfolio.price).label("sum-price")).all()
    #This finds the average price of all the investments 
    avgPrice = db.session.query(func.avg(InvestmentPortfolio.price).label("avg-price")).all()

    #Pass the variables into the invest.html backend for this page so that they can be displayed to the user
    return render_template('invest.html', title='Invest',
    form3=form3,
    form1=form1, 
    user_info=user_info, 
    len_user_info=len_user_info, 
    profile_picture=profile_picture,
    sorted_percentage_change=sorted_percentage_change,
    len_sorted_percentage_change=len_sorted_percentage_change,
    sumPrice = sumPrice,
    avgPrice = avgPrice)

#Creates the connection from the front end to the backend for the download function
@app.route('/download', methods=['GET', 'POST']) #Accepts post and get requests made by the user
def download():

        #Open the protfolio.txt file in write mode so that any previous data in the file will be deleted
        investments = open("tickermain/static/client/portfolio.txt" , 'w+')
        #Append the titles of each column for the user
        investments.write('Id, Username, Stock, Ticker, Value, Change, Percentage Change, Date \n')
        #Get all data about the users investment portfolio
        investment_data = InvestmentPortfolio.query.filter_by(username=current_user.username).all()
        #Loop through each row in the investment portfolio database and add each row on a new line in the file with each element being seperated by a comma 
        for i in range(len(investment_data)):
            investments.write(str(investment_data[i].id) + ', ')
            investments.write(investment_data[i].username + ', ')
            investments.write(investment_data[i].stock + ', ')
            investments.write(investment_data[i].symbol + ', ')
            investments.write(str(investment_data[i].price) + ', ')
            investments.write(str(investment_data[i].profit_loss) + ', ')
            investments.write(str(investment_data[i].change)+ ', ')
            investments.write(investment_data[i].original_date + ', \n')
        
        #Exeption handling - try to close the file and upload it to the users machine
        try:
            investments.close()
            return send_from_directory(app.config['UPLOAD_FOLDER'], 'portfolio.txt', as_attachment=True)

        #Otherwise, if the file is corrupted, close it and redirect the user to the error 404 page
        except FileNotFoundError:
            investments.close()
            abort(404)

#Creates the connection from the front end to the backend for the register page
@app.route('/register', methods=['GET', 'POST']) #Accepts post and get requests made by the user
def register():
        
    #Starts the timer - used for measuring the page loading times
    start = time.perf_counter()

    #If the user is already logged in, they have an account already therefore there is no need to register an account
    #They are redirected to the home page
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    #Retrieve the data from the registration form
    form = RegistrationForm()
    #If the data retrieved is valid
    if form.validate_on_submit():
        #Peform a hashing algorithm on the password using the password_hashing.py file
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        #Add the new users credentials to the user database
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        #Commit the changes made to the database
        db.session.commit()
        #Alert the user that their account ha been successfully created 
        #flash(f'Account created for {form.username.data}!', 'success')
        #Redirect them to the login page so that they can login to the account they just created
        return redirect(url_for('login'))
    #Stop the loading time counter as this page has fully loaded 
    finish = time.perf_counter()
    #print(f'Finished in {round(finish-start, 2)} second(s)')
    #Renders the page for the user and passes in the form data to be used in the backend 
    return render_template('register.html', title='Register', form=form)


#Creates the connection from the front end to the backend for the login page
@app.route('/login', methods=['GET', 'POST']) #Accepts post and get requests made by the user
def login():

    #If the user is already logged in, there is no need to login again so redirect them to the home page 
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    #Get the data from the login form and store it as a variable 
    form = LoginForm()
    #If the data enetered by the user is valid
    if form.validate_on_submit():
        #Checks if the username already exists in the database
        user = User.query.filter_by(username=form.username.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            #Otherwise login in the user and remeber the user if theu tick the remember me check box
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            #Redirects them to the page they were previously on, otherwise redirect them to the home page
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            #Alert the user that they have logged in successfully
            flash('Login unsuccessful', 'danger')
    
    #Renders the page for the user and passes in the form data to be used in the backend 
    return render_template('login.html', title='Login', form=form)

#Logout link which logs the current user out and redirects them to the home page
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

#Creates the connection from the front end to the backend for the account page
@app.route('/account', methods=['GET', 'POST']) #Accepts post and get requests made by the user
@login_required
def account():

    #Starts the timer - used for measuring the page loading times
    start = time.perf_counter()

    #Gets the data entered from the update form
    form = UpdateForm()
    #If the data entered is valid
    if form.validate_on_submit():
        #Replace the current users old username with the new username that they entered and want to change to 
        old_username = current_user.username
        #Replace the current users old email with the new email that they entered and want to change to 
        old_email = current_user.email
        #If they have enetered a new profile picture
        if form.picture.data:
            #Save the picture to the sytem so it can be accessed when needed again
            picture_file = save_picture(form.picture.data)
            #Replace the current users old profile picture with their new one
            current_user.image_file = picture_file

        #Replace the current users credentials with the updated ones
        current_user.username = form.username.data
        current_user.email = form.email.data
        #Commit the updates to the database
        db.session.commit()
        #Alert the user that they have successfully updated their account information 
        flash('Your account has been updated', 'success')

        #Gets all the rows in the investment portfolio database contains the users old username
        user_info = InvestmentPortfolio.query.filter_by(username=old_username).all()
        #Updates these old usernames so that the now contain the users new database (this means all of th eusers investments are carried over)
        for i in range(len(user_info)):
            user_info[i].username = current_user.username
            #Commit these updates to the database
            db.session.commit()
            #This updates the portfolio database so that when the username is changed the user keeps all of their investments showing
        #Refresh the page
        return redirect(url_for('account'))
    
    #When the page is loaded, fill the form fields witht he current user account details in the entry areas (acts as placeholders)
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    #Initialises the users account profile picture
    if current_user.is_authenticated:
        profile_picture = url_for('static', filename='profilepicture/' + current_user.image_file)
    else:
        profile_picture = 'default_img.jpg'
    
    #Stop the loading time counter as this page has fully loaded 
    finish = time.perf_counter()
    #print(f'Finished in {round(finish-start, 2)} second(s)')
    #Renders the page for the user and passes in the form data to be used in the backend 
    return render_template('account.html', title='Account', 
    form=form, 
    profile_picture=profile_picture)

#Creates the connection from the front end to the backend for the account page
@app.route('/recommend', methods=['GET', 'POST']) #Accepts post and get requests made by the user
@login_required
def recommend():
    
    #Starts the timer - used for measuring the page loading times
    start = time.perf_counter()

    #If the current user has permissions and is logged in
    #Update profile picture
    if current_user.is_authenticated:
        profile_picture = url_for('static', filename='profilepicture/' + current_user.image_file)
    else:
        profile_picture = 'default_img.jpg'
    
    #Uses the subroutine find_recommended stocks to assign an array of stocks to the variable stock_info
    stock_info = find_recommended_stocks(6, True)
    #Gets the name of the stock and other data about it
    recommendedStocks = stock_info[0]
    volume = stock_info[1]
    adj_close = stock_info[2]
    company_names=stock_info[3]


    len_recommendedStocks = len(recommendedStocks)
    #Fetch the stocks adjacent close graphs and assign them to a variable 
    graphs = os.listdir('/Users/benjaminhardy/Ticker/tickermain/static/images/recommendations')

    #Stop the loading time counter as this page has fully loaded 
    finish = time.perf_counter()
    #print(f'Finished in {round(finish-start, 2)} second(s)')

    #Pass the variables intot he backend
    return render_template('recommend.html',
    profile_picture=profile_picture,
    recommendedStocks=recommendedStocks,
    len_recommendedStocks=len_recommendedStocks,
    graphs=graphs,
    volume=volume,
    adj_close=adj_close,
    company_names=company_names)


#Create custom error pages 
#404 error - when trying to access a page that doesnt exist
@app.errorhandler(404)
def error_404(error):
    if current_user.is_authenticated:
        profile_picture = url_for('static', filename='profilepicture/' + current_user.image_file)

    else:
        profile_picture = 'default_img.jpg'
    return render_template("errors/404.html", profile_picture=profile_picture), 404

#403 error - when you are trying to access something that you do not have the correct permissions 
@app.errorhandler(403)
def error_403(error):
    if current_user.is_authenticated:
        profile_picture = url_for('static', filename='profilepicture/' + current_user.image_file)

    else:
        profile_picture = 'default_img.jpg'
    return render_template("errors/403.html", profile_picture=profile_picture), 403

#Error due to server crashing or not handling a commit 
@app.errorhandler(500)
def error_500(error):
    if current_user.is_authenticated:
        profile_picture = url_for('static', filename='profilepicture/' + current_user.image_file)

    else:
        profile_picture = 'default_img.jpg'
    return render_template("errors/500.html", profile_picture=profile_picture), 500

'''

#If it is the start of a new week
if check_if_new_week() == True:

    #Send email using the smtp API
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls() #encrypts traffic
        smtp.ehlo() #run as encrypted connection
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        #Content of the email
        recommendedStocks = find_recommended_stocks(5, False)[0] #saves loading time by setting graph = False so program doesnt waist time creating graph
        seperator = ', '
        email_stocks = seperator.join(recommendedStocks)
        topic = 'Weekly stock recommendations'
        body = f'Hi, your weekly stock recommendations are as follows: {email_stocks}'

        email_message = f'Subject: {topic}\n\n{body}'

        #Select all emails on the mailing list and send the newsletter to them
        emails = mailingList.query.all()
        for i in range(len(emails)):
            smtp.sendmail(EMAIL_ADDRESS, emails[i].email, email_message)
            print('email sent')
'''


'''Interlink the chatbox and the user and the investment portfolio so that when the username is changed, the username changes for each table
TSLA Amazon and newsfeed not updating
'''

#214 214 214




'''
    ALTERNATIVE WAY
    if form4.validate_on_submit() and current_user.is_authenticated:
        search = form4.search.data
        file = open("tickermain/tickerlist.txt", "r")
        for line in file:
            if search in line.split(',')[2]:
                company_name = line.split(',')[0]
        
        if company_name is None:
            flash(f'No results found for: { search }!', 'Danger')
            url = "https://www.bbc.co.uk/search?q=Amazon" + "+shares"
            company_name='AMZN'
            search = 'Amazon'
            return redirect('home')
        
        else:
            url = "https://www.bbc.co.uk/search?q=" + search + "+shares"
            print(search, 'hey')
        
        file.close()
    
        updateGraph(search, company_name)
        predictGraph(search, company_name)

    else:
        url = "https://www.bbc.co.uk/search?q=Amazon" + "+shares"
        company_name='AMZN'
        search = 'Amazon'
        updateGraph('AMZN', 'AMZN')
        predictGraph('AMZN', 'AMZN')

    '''