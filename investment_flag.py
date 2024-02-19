import numpy as np
#Function used to determine the stages when the stock should be bought and sold whilst investing
def buyOrSell(data):
    #Create empty arrays and placeholder variable 
    signalBuy =[]
    signalSell = []
    active = -1
    #The active variable is used to determine if it is already in a ceratain phase
    #For instance, there would be no point in indicating a buy phase if it is already in a buy phase
    #Loop through the ajacent close for the stock (this is in the form of a list) 
    for i in range(len(data)):
        #If the value for the short rolling average is greater than the same position for the long rolling average
        if data['shortA'][i] > data['longA'][i]:
            #Check the status of active placeholder
            if active != 1:
                active = 1
                #Add a buy phase to the signal buy list to indicate the user should buy here 
                #This indicates a change in momentum has occured 
                signalBuy.append(data['Ticker'][i])
                #Add a nan value to the signal sell list
                signalSell.append(np.nan)
            else:
                #Append nan to both
                signalBuy.append(np.nan)
                signalSell.append(np.nan)
        #If the value for the short rolling average is lower than the same position for the long rolling average
        elif data['shortA'][i] < data['longA'][i]:
            #Check the status of active
            if active != 0:
                active = 0
                #Append a nan value to the signal buy phase
                signalBuy.append(np.nan)
                #Add a sell phase to the signal sell list to indicate the user should sell here 
                #This indicates a change in momentum has occured 
                signalSell.append(data['Ticker'][i])
            else:
                #Otherwise append a nan value to both lists
                signalBuy.append(np.nan)
                signalSell.append(np.nan)
        else:
            #Otherwise append a nan value to both lists
            signalBuy.append(np.nan)
            signalSell.append(np.nan)
    #Return the two lists which contain elements for the position to buy and sell for the inputed stock
    return(signalBuy, signalSell)
#This function is used to determine if a stock is in a buy or a sell phase
def investmentStage(data):
    #Create empty arrays
    sellPrices = []
    buyPrices = []
    sellTimes = []
    buyTimes = []
    #Loop through the signal buy and signal sell lists
    #Select the last phase from the signal buy phase and the signal sell phase (most recent)
    for i in range(len(data['activateSell'])):
        if np.isnan(data['activateSell'][i]) == False:
            sellTimes.append(data.index[i])
        if np.isnan(data['activateBuy'][i]) == False:
            buyTimes.append(data.index[i])
    #Select the last value from these arrays
    lastSell = sellTimes[-1:]
    lastBuy = buyTimes[-1:]
    #Which ever date is the most recent, this is the phase the stock is in so return the appropriate phase
    if lastSell > lastBuy:
        return('SELL')
    else:
        return('BUY')
