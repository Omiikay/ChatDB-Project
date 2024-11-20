from flask import Flask, render_template, request, jsonify, url_for
from flask_pymongo import PyMongo
from bson import BSON
from application import constant
import json
import pandas as pd
from application import mongoApi, chatBot
from application import app, mongo, MONGO_URI, DB_NAME

'''
# MongoDB Settings
MONGO_URI = constant.MONGO_URI
DB_NAME = constant.DB_NAME

# Initialize Flask app
app = Flask(__name__)

# MongoDB setup
app.config['DEBUG'] = True
app.config["MONGO_URI"] = MONGO_URI #+ "/analysis"
mongo = PyMongo(app).cx[DB_NAME] # DB_NAME = ’analysis‘
'''

# Initialize chatbot
bot = chatBot.MenuBot()

# HomePage
@app.route("/")
def index():
    return render_template('index.html')

# Upload API
@app.route("/save_upload", methods=["POST"])
def save_upload():
    try:
        inputFile = request.files.get("file")
        # Loading or Opening the json file
        if inputFile:
            # to Mongo
            file_name = inputFile.filename.split('.')[0]
            
            # mongoApi.save_upload(inputFile)

        return jsonify({
            'message': f"Successfully uploaded csv files into collection: {file_name} in db: {DB_NAME}."
        }), 200
    
    except Exception as e:
        return jsonify({'upload error!': str(e)}), 500
    
# find
@app.route("/find", methods=["GET"])
def find_query():
    query_find = "{'PostalCode': '14111'}"
    return jsonify(mongoApi.find(DB_NAME, 'AdventureWorks_CustomerMaster', query_find)), 200

# current default api
@app.route('/get_response', methods=['POST'])
def get_bot_response():
    user_input = request.form['user_input']
    # print(user_input)
    response = bot.process_message(user_input)
    print('received successfully')
    print(response)
    return response

if __name__ ==  "__main__":
    app.run(port=5001)