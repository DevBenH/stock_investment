import matplotlib.pyplot as plt                            
from pandas_datareader import data as pdr                         
from pandas_datareader._utils import RemoteDataError       
from datetime import datetime, timedelta
import numpy as np
import yfinance as yf
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pandas as pd


def updateGraph(search, company_name):

    def create_plot(stock_data, ticker, filename):

        #Use the data to plot the graph
        stats = get_stats(stock_data)
        #Graph style format
        plt.style.use('fivethirtyeight')
        #Graph dimensions
        plt.figure(figsize=(16,8))
        #Graph data values and label 
        plt.plot(stock_data, label=ticker)
        #X-axis and y-axis names
        plt.xlabel('Date')
        plt.ylabel('Adj Close (p)')
        plt.legend()
        #Title of the graph
        plt.title('Stock Price over Time')
        #Save the graph to the system in the static images folder
        plt.savefig('/Users/benjaminhardy/Ticker/tickermain/static/images/' + filename + '.png')


    def get_stats(stock_data):
        #Get each stock data
        return {
            'last': np.mean(stock_data.tail(1)),
            'short_mean': np.mean(stock_data.tail(20)),
            'long_mean': np.mean(stock_data.tail(200)),
            'short_rolling': stock_data.rolling(window=20).mean(),
            'long_rolling': stock_data.rolling(window=200).mean()
            }


    def clean_data(stock_data, col):
        #Clean the data so it can be used in graph formatting
        weekdays = pd.date_range(start=start_date, end=end_date)
        clean_data = stock_data[col].reindex(weekdays)
        return clean_data.fillna(method='ffill')

    #This creates the graph over 15 years
    start_date = '2005-01-01'
    end_date = str(datetime.now().strftime('%Y-%m-%d'))
    yf.pdr_override()
    data = pdr.get_data_yahoo(company_name, start=start_date, end=end_date)
    adj_close = clean_data(data, 'Adj Close')
    create_plot(adj_close, company_name, '15years')

    #This creates the graph over the past 5 days
    start_date = str((datetime.now()-timedelta(days=31)).strftime('%Y-%m-%d'))
    data = pdr.get_data_yahoo(company_name, start=start_date, end=end_date)
    adj_close = clean_data(data, 'Adj Close')
    create_plot(adj_close, company_name, '1month')



def predictGraph(search, company_name):
    
    #Graph styling format
    plt.style.use('fivethirtyeight')

    #Set time retraints
    end_date = str(datetime.now().strftime('%Y-%m-%d'))
    start_date = str((datetime.now()-timedelta(days=366)).strftime('%Y-%m-%d')) 

    #Get stock data for required company
    df = pdr.get_data_yahoo(company_name, start=start_date, end=end_date)

    #Set the amount of days its predicting for to 120
    future_days = 120
    #Allocate room for these 120 days in the dataframe
    df['Prediction'] = df[['Close']].shift(-future_days)

    #Create numpy arrays with future days and dataframe
    x = np.array(df.drop(['Prediction'], 1))[:-future_days]
    y = np.array(df['Prediction'])[:-future_days]

    #Create the variable trains for machine learning (used to train the data)
    x_train, y_train = train_test_split(x, y, test_size = 0.25)

    #Create two types of machine learning graphs - linear regression and decision tree regression
    tree = DecisionTreeRegressor().fit(x_train, y_train)
    lr = LinearRegression().fit(x_train, y_train)

    #Get predicition values using previous stock data
    x_future = df.drop(['Prediction'], 1)[:-future_days]
    x_future = x_future.tail(future_days)
    x_future = np.array(x_future)

    #Append the predicted values to one variable
    #In this case I have decided to create the linear regression lines as well as the decision tree regression 
    #However I will only be outputing the decision tree regression graph in my system
    tree_prediction = tree.predict(x_future)
    lr_prediction = lr.predict(x_future)

    predictions = tree_prediction
    #Create required dataframe
    valid = df[x.shape[0]:] 
    #Assign predictions to dataframe
    valid['Predictions'] = predictions

    #Assign the correct dimensions to the graph
    plt.figure(figsize=(16,8))
    #Label the graphs axis and give it a title
    plt.title('Prediction')
    plt.xlabel('Days')
    plt.ylabel('Close Price')
    #Plot the close values on the y-axis
    plt.plot(df['Close'])
    #Plot dataframe values
    plt.plot(valid[['Close', 'Predictions']])
    plt.legend(['Original', 'Value', 'Predicted'])
    #Save the graph to the system
    plt.savefig('/Users/benjaminhardy/Ticker/tickermain/static/images/predictgraph.png')




