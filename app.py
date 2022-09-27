from flask import Flask, render_template, request
import pymongo
import json
import constants

app = Flask(__name__)



myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["PoolRankings"]

# if(db.get_collection("Records")):
#     records = db.get_collection('Records')
# else:

records = db.Records
result = records.insert_one({"Name": "Jonathan", "Rating": constants.StartingRating, "Matches": "0" })
print(result)

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


    # checks to see if name exists in database already
    # if records.find({}):
    #     print("in If statement")
    #     for record in records.find({}):
    #         print("in for loop")
    #         print(record)
    #         if record['Name'] == nameToBeAdded:
    #             #fix error code
    #             print("name found")
    #             return 'false', 418
    print("just before insert")   
    db.records.insert_one({"Name": nameToBeAdded, "Rating": constants.StartingRating, "Matches": "0" })
    print("At the end")
    return 'done', 201


    