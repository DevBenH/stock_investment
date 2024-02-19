import os
import secrets 
from tickermain import app

def save_picture(form_picture):
    #Creates a random 8-bit hexadecimal value
    random_hex = secrets.token_hex(8)
    #Creates the path filename
    _, f_ext = os.path.splitext(form_picture.filename)
    #Concatenates the filename with the hexadecimal value which is used to make sure each filename is unique
    picture_filename = random_hex + f_ext
    #Creates the valid path in order to save the file
    picture_path = os.path.join(app.root_path, 'static/profilepicture', picture_filename)
    #Saves the picture to the required path
    form_picture.save(picture_path)
