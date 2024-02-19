import hashlib
import os

#Function used to create the hashed password
def create_hashed_password(password):
    #Create salt from a random number with 50 characters
    salt = os.urandom(50)
    #Hash the password using the created salt and sha256
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    #Return the key and the salt 
    return salt, key

#Function used to check the password entered is the correct password
def check_hashed_password(password, key, salt):
    #Get the required hashed password
    key_identifier = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    #Check it matches to the key entered
    if key == key_identifier:
        #If it is correct return True
        return True
    else:
        #Otherwise return False
        return False


