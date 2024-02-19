import math

#This subroutine calculates the product moment correlation coefficient formula 
#The formula for this is shown is the design section
def calculatePmcc(y):

    x = []
    for i in range(len(y)):
        x.append(i)
       
    x_average = sum(x)/len(x)
    y_average = sum(y)/len(y)

    new_x = []
    new_y = []
    for i in range(len(x)):
        new_x.append(x[i] - x_average)
        new_y.append(y[i] - y_average)
            
    squared_x = []
    squared_y = []
    for i in range(len(new_x)):
        squared_x.append((x[i] - x_average)*(x[i] - x_average))
        squared_y.append((y[i] - y_average)*(y[i] - y_average))

    multiply_xy = []
    for i in range(len(new_x)):
        multiply_xy.append(new_x[i] * new_y[i])

    sxy = sum(multiply_xy)
    sxx = sum(squared_y)
    syy = sum(squared_x)

    pmcc_value = (sxy/math.sqrt(syy*sxx))

    return round((pmcc_value * 100),0)
