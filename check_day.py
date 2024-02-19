from datetime import datetime, timedelta
from tickermain.models import InvestmentPortfolio

#Subroutine used for indicating when it is a new day 
#If it is a new day, the investment details need to be updated as the stock values would have changed
def check_if_new_day():
    #Get the data today in an appropriate format
    date_today = str(datetime.now().strftime('%Y-%m-%d'))
    #Select all dates in the users investments database
    user_info = InvestmentPortfolio.query.filter_by().all()
    
    #Loop through these dates in the database
    for i in range(len(user_info)):
        #If any of them are not equal to todays date
        if user_info[i].date != date_today:
            #If new day return true
            return True
        else:
            #Otherwise return false
            return False

#Subroutine used for checking if it is a new week
#Used as an indicator to when the newsletter needs to be sent out
def check_if_new_week():
    #Get the day of the week as an integer value (Monday = 0, Sunday = 6)
    day_of_week = datetime.today().weekday() 
    #If the day of the week is equal to the integer value for Wednesday
    if day_of_week == 2:   
        return True
    else:
        return False
