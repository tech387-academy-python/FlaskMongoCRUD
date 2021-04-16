from flask import Flask, request, json, Response, jsonify
from pymongo import MongoClient
import mysql.connector

app = Flask(__name__)

def getMysqlConnection():
    return mysql.connector.connect(user='root', host='python_db_1', port='3306', password='root', database='ChargerDatabase')

class MongoAPI: 
    def __init__(self, data):
        self.client = MongoClient("mongodb://mymongo_1:27017/")

        database = data['database']
        collection = data['collection']
        cursor = self.client[database]
        self.collection = cursor[collection]
        self.data=data

    def read(self):
        documents = self.collection.find()
        output = [{item: data[item] for item in data if item != '_id'} for data in documents]
        return output

    def write(self, data):
        new_document = data['Document']
        response = self.collection.insert_one(new_document)
        output = {'Status': 'Successfully Inserted',
                  'Document_ID': str(response.inserted_id)}
        return output

    def update(self):
        filt = self.data['Filter']
        updated_data = {"$set": self.data['DataToBeUpdated']}
        response = self.collection.update_one(filt, updated_data)
        output = {'Status': 'Successfully Updated' if response.modified_count > 0 else "Nothing was updated."}
        return output

    def delete(self, data):
        filt = data['Filter']
        response = self.collection.delete_one(filt)
        output = {'Status': 'Successfully Deleted' if response.deleted_count > 0 else "Document not found."}
        return output

data1 = {
        "database": "cat_app",
        "collection": "cats",
       } 


# SETTING UP FLASK SERVER 
@app.route('/')
def base():
    return Response(response=json.dumps({"Status": "UP"}),
                    status=200,
                    mimetype='application/json')
  
# ROUTES
@app.route('/sql', methods=['GET'])
def get_months():
    try:
        dbb = getMysqlConnection()
        print(dbb)
            
        sqlstr = "SELECT * from SiteData"
        print(sqlstr)
        cur = dbb.cursor()
        cur.execute(sqlstr)
        output_json = cur.fetchall()
    except Exception as e:
        print("Error in SQL:\n", e)
    finally:
        dbb.close()
    return jsonify(results=output_json)


@app.route('/mongodb', methods=['GET'])
def mongo_read():
    data = {
        "database": "cat_app",
        "collection": "cats",
       } 
    if data is None or data == {}:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.read()
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')

@app.route('/mongodb', methods=['POST'])
def mongo_write():
    data = {
        "database": "cat_app",
        "collection": "cats",
        "Document":{
            "name": "best cat",
            "age": 100, 
            "temperament": "wild",
        }
    }
    # if data is None or data == {} or 'Document' not in data:
    #     # return Response(response=json.dumps({"Error": "Please provide connection information"}),
    #     #                 status=400,
    #     #                 mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.write(data)
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')

@app.route('/mongodb', methods=['PUT'])
def mongo_update():
    data = {
        "database": "cat_app",
        "collection": "cats",
        "Filter": {
            "name": "best cat"
        },
        "DataToBeUpdated": {
            "age": 80
        }
}
    if data is None or data == {} or 'Filter' not in data:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.update()
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')


@app.route('/mongodb', methods=['DELETE'])
def mongo_delete():
    data = {
        "database": "cat_app",
        "collection": "cats",
        "Filter": {
            "name": "best cat"
        }
        }
    if data is None or data == {} or 'Filter' not in data:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.delete(data)
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')





#Running App
if __name__ == '__main__':
    app.run(debug=True, port=5001, host='localhost')
    
    # mongo_obj = MongoAPI(data)
    # print(json.dumps(mongo_obj.read(), indent=4))