
import json
from pydoc import render_doc
import constants
from flask import Flask, render_template, request
import pymongo

app = Flask(__name__)

# if __name__=='__main__':
#     app.run(debug=False, host='0.0.0.0')



myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["PoolRankings"]
if(db.get_collection("Records")is not None):
    records = db.get_collection('Records')
else:
    print("No Records collection found. Check database settings")
    exit()


records = db.Records




@app.route('/')
def hello():
    return render_template("index.html")

@app.route('/ReportMatch')
def reportMatch_page():
    return render_template('reportMatch.html')


def calculate_expected(player1, player2):
    return (1/(1+(10**( (records.find_one({'Name':player2})['Rating'] - records.find_one({'Name':player1})['Rating'])/constants.D))))



@app.route('/addMatchToDatabase', methods = ["POST"])
def report_match():
    data=request.form

    player1 = data.get("PlayerName1")
    player2 = data.get("PlayerName2")
    winner = data.get("Winner")
    player1_expected = calculate_expected(player1, player2)
    player2_expected = calculate_expected(player2, player1)
    if(winner==player1):
        result = (1,0)
    elif(winner==player2):
        result = (0,1)
    else:
        return 400

    records.update_one({"Name":player1},{"$set" :{"Rating": (records.find_one({"Name":player1})['Rating'] + constants.K*(result[0]-player1_expected))}})
    records.update_one({"Name":player2},{"$set" :{"Rating": (records.find_one({"Name":player2})['Rating'] + constants.K*(result[1]-player2_expected))}})

    print(records.find_one({"Name": player1}))
    print(records.find_one({"Name": player2}))
    return 'done' , 200


@app.route('/addNewPlayer', methods = ["POST"])
def addNewPlayer():
    #processes request to get data
    data = request.form
    #saves name that needs to be added
    nameToBeAdded = data['PlayerName']


    # checks to see if name exists in database already
    if records.find({}):
        for record in records.find({}):
            if record['Name'] == nameToBeAdded:
                #fix error code
                return 'false', 418  
    db.Records.insert_one({"Name": nameToBeAdded, "Rating": constants.StartingRating, "Matches": "0" })
    return 'done', 201


    
if __name__=='__main__':
    app.run(debug = True, host='0.0.0.0')
