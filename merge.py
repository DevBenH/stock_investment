data = []


def splitMerge(data):
    #If the data contains less than 1 element, it is already sorted
    if len(data) <= 1:
        return data

    #Split the array into two halves and uses recurssion to repeat this process until it is an array with only two elements
    holdLeft = splitMerge(data[:len(data)//2])
    holdRight = splitMerge(data[len(data)//2:])

    #Calls the other function and passess in the two halves of the array
    return sortMerge(holdLeft, holdRight)


def sortMerge(holdLeft, holdRight):
    sorted_list = []

    #Assigns placeholders for the array
    i, j = 0, 0

    #Sorts the array using a merge sort
    while len(holdLeft) > i and len(holdRight) > j:
        if holdLeft[i] < holdRight[j]:
            sorted_list.append(holdLeft[i])
            i += 1
        else:
            sorted_list.append(holdRight[j])
            j += 1

    sorted_list += holdLeft[i:]
    sorted_list += holdRight[j:]
    #Returns the sorted array
    return sorted_list


print(splitMerge(data))