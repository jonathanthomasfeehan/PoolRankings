from flask import Flask, render_template, request
import pymongo
import json
import constants

app = Flask(__name__)



myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["PoolRankings"]
records = db.get_collection('Records')


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/addNewPlayer', methods = ["POST"])
def addNewPlayer():
    #processes request to get data
    data = request.form
    print(data)
    #saves name that needs to be added
    nameToBeAdded = data['PlayerName']


    #checks to see if name exists in database already
    if records.find({}):
        for record in records.find({}):
            if record['Name'] == nameToBeAdded:
                #fix error code
                return 'false', 418
                
    db.records.inset({"Name": nameToBeAdded, "Rating": constants.StartingRating, "Matches": "0" })
    return 'done', 201


    