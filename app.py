'''
File name: app.py
Function: 
Comment: main file.
'''

from flask import render_template, request, jsonify
import pandas as pd
from typing import List
from application.mongo_component import mongoApi
from application import chatBot
from application.mysql_component import mysqlApi
from application import app, DB_NAME
from application.toolkit.sampleGenerator import Table , SampleBuilder

# Initialize chatbot
bot = chatBot.MenuBot()

# HomePage
@app.route("/")
def index():
    return render_template('index.html')

# Upload API for Mongo and Mysql
@app.route("/save_upload", methods=["POST"])
def save_upload():
    try:
        inputFiles = request.files.getlist("file")
        file_names = []
        
        if inputFiles:
            tables: List[Table] = []
            for inputFile in inputFiles:
                file_name = inputFile.filename.split('.')[0]
                file_names.append(file_name)
                table = get_table_item(inputFile, file_name)
                tables.append(table)
                # print(table.tableName)
                # print(inputFile.content_type)
                mongoApi.save_upload(inputFile, table.df) 
                # mysqlApi.save_upload_mysql(inputFile, table.df)

            # init bot.query_builder
            bot.sample_generator = SampleBuilder()
            bot.sample_generator.tables = tables

        if file_names:    
            names = '\n - '.join(file_names)
            return jsonify({
                "status": "success",
                'message': f"Successfully uploaded files into Databases\n" \
                           f"\nThe following tables have been created:\n - {names}" \
                           f"\n\n Now! Type anything to Home page!"
            }), 200
    
    except Exception as e:
        return jsonify({'upload error!': str(e)}), 500
    
# Mongo find
@app.route("/find", methods=["GET"])
def find_query():
    query_find = "{'PostalCode': '14111'}"
    query_find2 = "{'AddressID': 2}"
    return jsonify(mongoApi.find(DB_NAME, 'AdventureWorks_CustomerMaster', query_find2)), 200

# find some sample
@app.route("/findAll", methods=["GET"])
def find_all_query():
    return jsonify(mongoApi.find_all(DB_NAME, 'user')), 200


# current default api
@app.route('/get_response', methods=['POST'])
def get_bot_response():
    user_input = request.form['user_input']
    # print(user_input)
    response = bot.process_message(user_input)
    print('received successfully')
    #print(response)
    return response

#stop current session
@app.route('/kill', methods=['POST'])
def kill():
    try:
        bot.exit_chat()
        return jsonify({
            "status": "success",
            "message": "Chat Reset!"
        }), 200
    except Exception as e:
        print(e)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    

def get_table_item(inputFile, file_name: str) -> Table:
    df = pd.read_csv(inputFile)
    char_columns = df.select_dtypes(include=['object', 'string']).columns.tolist()
    num_columns = df.select_dtypes(include=['number']).columns.tolist()
    table = Table(
            tableName = file_name,
            fields_str = char_columns,
            fields_num = num_columns,
            df = df
    )
    return table

if __name__ ==  "__main__":
    app.run(port = 5001)