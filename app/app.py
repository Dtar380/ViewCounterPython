#####     IMPORTS     #####
from os.path import exists, isfile
from os import makedirs, umask
from flask import Flask, request
from requests import get
import json

#####    CONSTANTS    #####
GITHUB = "https://github.com" # Github url as a constant
FILE_PATH = "database.json"

#####    VARIABLES    #####
app = Flask(__name__) # Flask app

#####    FUNCTIONS    #####
# Checks if user and/or repo exist
def check_url(user: str, repo: str = None) -> list:

    # Check if user and repo exists if given
    if user and get(f"{GITHUB}/{user}").status_code != 200:
        return [False, "User does not exist"]
    if repo and get(f"{GITHUB}/{user}/{repo}").status_code != 200:
        return [False, "Repo does not exist"]
    
    return [True, 200]

# Reads the count without updating it
def read_count(user: str, repo: str = None) -> str:

    # Read the file
    with open(FILE_PATH, "r+") as f:
        data = json.load(f)

    # Check if the user and/or repo is on the database
    if user not in data.keys():
        return {"status": 404, "message": "No user found on database"}
    elif repo and repo not in data[user]["repos"].keys():
        return {"status": 404, "message": "No repo found on database"}

    # If no repo was provided return the user total views
    if not repo:
        return {user: data[user][user]}
    # If repo was provided return repo total views
    else:
        return {repo: data[user]["repos"][repo]}

# Updates the count on the given username + repo/user
def update_count(user: str, repo: str = None) -> int:

    # Open the file and read the value
    with open(FILE_PATH, "r+") as f:
        data = json.load(f)

    # Check if user is already in the DataBase
    if not user in data.keys():

        # Create a key with the username and add 1 view to the username
        # And if a repo was provided add one view to the repo too
        data[user] = {
            user: 0,
            "repos": {}
        }

    # Update the user total view count
    data[user][user] = data[user][user] + 1

    # If a repo was provided
    if repo:
        # And was already listed add 1 and set that value to number var
        if repo in data[user]["repos"].keys():
            data[user]["repos"][repo] = data[user]["repos"][repo] + 1
            number = data[user]["repos"][repo]
        # If it didn't exist set both the repo and number value to 1
        else:
            data[user]["repos"][repo] = 1
            number = data[user]["repos"][repo]

    # If no repo was provided
    else:
        # Set the number to the user view count
        number = data[user][user]

    # Write new values
    with open(FILE_PATH, "w+") as f:
        json.dump(data, f)

    return number

# Function to transform long numbers to readable
def short_number(number: int) -> str:
    units = ["", "K", "M", "B", "T", "Q"] # Units up to Quadrillion

    # Iterate through all units
    for unit in units:
        if number <= 1000: # If the number is lower than 1000, break
            break
        number /= 1000 # Divide the number by 1000

    return f"{round(number, 1)}{unit}" # return the number with one rounded decimal and the unit in which it stopped

# transforms a dictionary into url
def url_from_params(params: dict) -> str:
    # Set an empty string
    message: str = ""

    # iterate through every item on the dict
    for key, value in params.items():
        # Add to the string a formated string with the format key=value&
        message += f"{key}={value}&"
    
    return message

# Creates the url for custom-icon-badges.demolab.com to later get the SVG
def retrieve_url(query, user: str, repo: str = None) -> str:

    # If theres only user query, update the user file, else update both repo and user
    if not repo:
        number = update_count(user)
    else:
        number = update_count(user, repo)

    # Generate parameters for the badge
    params = {
        "label": query.get("label") if query.get("label") else "Visitors",
        "labelColor": query.get("labelColor") if query.get("labelColor") else "C79600",
        "logo": query.get("logo") if query.get("logo") else "eye",
        "logoColor": query.get("logoColor") if query.get("logoColor") else "white",
        "message": short_number(number),
        "color": query.get("color") if query.get("color") else "E1AD0E",
        "style": query.get("style") if query.get("style") else "for-the-badge"
    }

    # Create a url for custom-icon-badges.demolab.com
    url = "https://custom-icon-badges.demolab.com/static/v1?" + url_from_params(params)

    return url

#####  APP FUNCTIONS  #####
# Returns the svg generated by custom-icon-badges.demolab.com
# for the view count of the repo given with the given query parameters
@app.route("/<user>/<repo>")
def give_views_url(user: str, repo: str):

    # Checks if the provided user and/or repo exists
    check_url_result = check_url(user, repo)
    if not check_url_result[0]:
        return {"status": 404, "message": check_url_result[1]}

    # Checks if onlyRead mode is enabled
    if request.args.get("onlyRead") == "True":
        # Returns the JSON format of views
        return read_count(user, repo)
    else:
        # Returns SVG badge
        return get(url=retrieve_url(request.args, user, repo)).text

# Returns the svg generated by custom-icon-badges.demolab.com
# for the view count of the user given with the given query parameters
@app.route("/<user>/")
def get_profile_views(user: str):

    # Checks if the provided user and/or repo exists
    check_url_result = check_url(user)
    if not check_url_result[0]:
        return {"status": 404, "message": check_url_result[1]}

    # Checks if onlyRead mode is enabled
    if request.args.get("onlyRead") == "True":
        # Returns the JSON format of views
        return read_count(user)
    else:
        # Returns SVG badge
        return get(url=retrieve_url(request.args, user)).text

# Index page
# Retrieves a status 200 code and a message in JSON format if everything is OK
@app.route("/")
def index():
    return {"status": 200, "message": "running"}

#####   RUN THE APP   #####
if __name__ == "__main__":
    # If the file does not exist create it
    if not exists(FILE_PATH):
        empty: dict = {} # Use empty dict to create the file
        with open(FILE_PATH, "x+") as f:
            json.dump(empty, f)

    # Run the flask app
    app.run(host="0.0.0.0", port=3000, debug=True)