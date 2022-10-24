
import json
from pydoc import render_doc
import constants
from flask import Flask, render_template, request
import pymongo
# TODO clean up excess imports

app = Flask(__name__)


#
# Uncomment when pushing to main, required for live build
#
# if __name__=='__main__':
#     app.run(debug=False, host='0.0.0.0')


#connect to database
myclient = pymongo.MongoClient("mongodb://localhost:27017/")

#select correct collection
db = myclient["PoolRankings"]

#checks to see if database exists
if(db.get_collection("Records")is not None):
    records = db.get_collection('Records')
else:
    print("No Records collection found. Check database settings")
    exit()

#assigns database collection to local variable
records = db.Records




@app.route('/')
def hello():
    #TODO fix function name
    #render homepage
    return render_template("index.html")

@app.route('/ReportMatch')
def reportMatch_page():
    #render match reporting page
    return render_template('reportMatch.html')


def calculate_expected(player1, player2):
    #calculate expected win rate using elo formula
    return (1/(1+(10**( (records.find_one({'Name':player2})['Rating'] - records.find_one({'Name':player1})['Rating'])/constants.D))))


### start of function to add player matches
@app.route('/addMatchToDatabase', methods = ["POST"])
def report_match():
    #Get data from post request
    data=request.form
    # 
    # TODO filter input
    #   
    # Get input
    player1 = data.get("PlayerName1")
    player2 = data.get("PlayerName2")
    winner = data.get("Winner")

    #Calculate expected win rates for both players
    player1_expected = calculate_expected(player1, player2)
    player2_expected = calculate_expected(player2, player1)

    #create tuple based on winner
    if(winner==player1):
        result = (1,0)
    elif(winner==player2):
        result = (0,1)
    #if winner is neither player or null return error code
    else:
        return "No winner selected" , 400

    #update database with new ratings
    records.update_one({"Name":player1},{"$set" :{"Rating": (records.find_one({"Name":player1})['Rating'] + constants.K*(result[0]-player1_expected))}})
    records.update_one({"Name":player2},{"$set" :{"Rating": (records.find_one({"Name":player2})['Rating'] + constants.K*(result[1]-player2_expected))}})

    #return successful code
    return 'done' , 200


@app.route('/addNewPlayer', methods = ["POST"])
def addNewPlayer():
    #processes request to get data
    data = request.form

    #saves name that needs to be added
    nameToBeAdded = data['PlayerName']

    # checks to see if name exists in database already
    # TODO look for better implementation, this was copied from previous project
    if records.find({}):
        for record in records.find({}):
            if record['Name'] == nameToBeAdded:
                # TODO fix error code
                return 'false', 418  
    #creats new record if one does not alreadt exist
    db.Records.insert_one({"Name": nameToBeAdded, "Rating": constants.StartingRating, "Matches": "0" })
    return 'done', 201


#use for local development
if __name__=='__main__':
    app.run(debug = True, host='0.0.0.0')
