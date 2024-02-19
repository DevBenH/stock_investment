import matplotlib.pyplot as plt                            
from pandas_datareader import data as pdr                         
from pandas_datareader._utils import RemoteDataError      
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import random

from .investment_flag import buyOrSell, investmentStage
from .pmcc import calculatePmcc


#This subroutine is used to find a shortlist of recommeded stocks
def find_recommended_stocks(limit, graph):
    #Initialise the time restraints 
    end_date = str(datetime.now().strftime('%Y-%m-%d'))
    start_date = str((datetime.now()-timedelta(days=1000)).strftime('%Y-%m-%d'))

    #Open the tickerlit.txt file 
    file = open("tickermain/tickerlist.txt", "r")
    #Set the empty arrays
    recommendedStocks =[]
    volume = []
    adj_close = []
    company_names = []
    count = 0

    #Read each line in the file containing the stock names and their corresponding ticker symbols
    lines = file.readlines()

    #Loop through these lines
    for line in lines:
        #Until the ammount of wanted stocks is reached
        if len(recommendedStocks) >= limit:
            break

        #Select a random line from the file (and so a random stock)
        random_line = random.choice(lines)
        #Split the line where the commas are
        random_stock = (random_line.split(',')[0])

        #Checks that there is not a fullstop in the ticker symbol (otherwise errors occur) 
        if "." not in random_stock:
            #Gets the stock data
            data = pdr.get_data_yahoo(random_stock, start=start_date, end=end_date)
            #Creates a pandas dataframe
            Ticker = pd.DataFrame()
            #Add the stocks adjacent close to the adjacent close on the dataframe
            Ticker['Adj Close'] = data['Adj Close']
            #Creates a short rolling average for the stock
            shortA = pd.DataFrame()
            #Rolling window 10 days
            shortA['Adj Close'] = data['Adj Close'].rolling(window=10).mean()
            #Creates a long rolling average for the stock
            longA = pd.DataFrame()
            #Rolling window 30 days
            longA['Adj Close'] = data['Adj Close'].rolling(window=30).mean()
            #Create a new data frame to store all the data
            data = pd.DataFrame()
            data['Ticker'] = Ticker['Adj Close']
            data['shortA'] = shortA['Adj Close']
            data['longA'] = longA['Adj Close']
            #Use buyOrSell subroutine to get data with buy and sell indicators in
            buy_sell = buyOrSell(data)
            data['activateBuy'] = buy_sell[0]
            data['activateSell'] = buy_sell[1]
            #Create new time restraints
            end_date = str(datetime.now().strftime('%Y-%m-%d'))
            start_date = str((datetime.now()-timedelta(days=31)).strftime('%Y-%m-%d')) 
            #Get stock data using the pandas datareader API  
            df = pdr.get_data_yahoo(random_stock, start=start_date, end=end_date)
            #Append value to lists and round them to 3 decimal places
            volume.append(round(df['Volume'][0],3))
            adj_close.append(round(df['Adj Close'][0],3))

            #If the stock is in a buy phase
            if investmentStage(data) == 'BUY':
                ticker_data = pdr.get_data_yahoo(random_stock, start=start_date, end=end_date)
                if len(ticker_data['Adj Close']) != 0:
                    #Calculate the product moment correlation coefficient value for the stock
                    #A higher value indicates a more reliable stock
                    element_pmcc = calculatePmcc(ticker_data['Adj Close'])
                    #Shortlist the stocks with a pmcc value above 40 (these tend to be more reliable stocks)
                    if element_pmcc >= 40:
                        
                        #Append this stock to the recommended stocks array
                        recommendedStocks.append(random_stock)
                        #Create the graph for the stock
                        if graph:
                            plt.style.use('fivethirtyeight')
                            plt.figure(figsize=(16,8))
                            plt.plot(ticker_data['Adj Close'], label=random_stock)
                            plt.xlabel('Date')
                            plt.ylabel('Adj Close (p)')
                            plt.legend()
                            plt.title('Stock Price over Time')
                            #Save the stock to the users device (so it can be accessed later on)
                            plt.savefig('/Users/benjaminhardy/Ticker/tickermain/static/images/recommendations/' + str(count) + '.png') 
                        count += 1   

    #For each stock in the recommended stocks array,append their ticker symbols to a seperate company names array
    for i in recommendedStocks:
        for line in lines:
            if i == line.split(',')[0]:
                    company_names.append(line.split(',')[2])

    #Return each variable created 
    return recommendedStocks, volume, adj_close, company_names
