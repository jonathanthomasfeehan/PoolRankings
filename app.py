
import json
import constants
from flask import Flask, render_template
import pymongo

app = Flask(__name__)

if __name__=='__main__':
    app.run(debug=False, host='0.0.0.0')
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["PoolRankings"]

if(db.get_collection("Records")is not None):
    records = db.get_collection('Records')
else:
    print("No Records collection found. Check database settings")
    exit()


#records = db.Records

@app.route('/')
def hello():
    return render_template("index.html")


@app.route('/addNewPlayer', methods = ["POST"])
def addNewPlayer():
    #processes request to get data
    data = request.form
    print(data)
    #saves name that needs to be added
    nameToBeAdded = data['PlayerName']


    # checks to see if name exists in database already
    if records.find({}):
        for record in records.find({}):
            if record['Name'] == nameToBeAdded:
                #fix error code
                return 'false', 418  
    db.records.insert_one({"Name": nameToBeAdded, "Rating": constants.StartingRating, "Matches": "0" })
    return 'done', 201


    
