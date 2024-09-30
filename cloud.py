import dropbox
import numpy as np

# Define Dropbox access token
token = '' # needs to be updated to keep working
# token = '' # You can comment out or remove this line if you're not using Dropbox

isonline = True # Set the variable to indicate online status

# Define function to retrieve data as a list from a CSV file
def get_as_list(file):
    global isonline
    try: # Attempt to connect to online leader board
        folder = '/Apps/Maze_game/' # Define folder path on Dropbox
        dpx = dropbox.Dropbox(token) # Initialize Dropbox object using token
        isonline = True
        path = folder + file + ".csv" # Construct file path
        _, dfile = dpx.files_download(path) # Download file from Dropbox
        return [line.split(',') for line in str(dfile.content.decode('utf-8')).split()] # Convert file content to list
    except:
        isonline = False
        folder = "scores/"
        path = folder + file + ".csv" # Construct file path
        f = open(path, mode='r') # Open file in read mode
        return [line.split(',') for line in f.read().split()] # Convert file content to list
# Define function to upload data as a numpy array to a CSV file
def upload_np(list, file):
    global isonline
    try:
        folder = '/Apps/Maze_game/' # Define folder path on Dropbox
        dpx = dropbox.Dropbox(token) # Initialize Dropbox object using token
        isonline = True
        asstr = ''
        for line in list: # Iterate over each line in the list
            asstr += line[0] + "," + line[1] + "\n" # Concatenate each line as a string
        dpx.files_upload(bytes(asstr, 'utf-8'), folder + file + ".csv", mode=dropbox.files.WriteMode(u'overwrite', None)) # Upload the string data to Dropbox
    except:
        folder = 'scores/'
        isonline = False
        asstr = ''
        for line in list: # Iterate over each line in the list
            asstr += line[0] + "," + line[1] + "\n" # Concatenate each line as a string
        path = folder + file + '.csv' # Construct file path
        f = open(path, mode="w") # Open file in write mode
        f.write(asstr) # Write string data to file
