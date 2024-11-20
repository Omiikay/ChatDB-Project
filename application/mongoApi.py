from application import constant, mongo, DB_NAME
from bson import json_util
import json
import pandas as pd

def save_upload(inputFile):
    # Loading or Opening the json file
    if inputFile:
        file_name = inputFile.filename.split('.')[0]
        match (inputFile.content_type):
            case constant.TYPE_JSON:
                records = list(map(json.loads, inputFile))
                if len(records) > 1:
                    # mongo.db[inputJson.filename].insert_many(inputJson)
                    mongo[f"analysis.{file_name}"].insert_many(records)
                else:
                    # mongo.db[inputJson.filename].insert_one(inputJson)
                    mongo[f"analysis.{file_name}"].insert_one(records)
            case constant.TYPE_CSV:
                '''
                TODO: support for csv input
                '''
                # convert csv to dict records format by pandas
                df = pd.read_csv(inputFile, encoding = 'ISO-8859-1')
                records = df.to_dict('records')

                if len(records) > 1:
                    mongo[f"{DB_NAME}.{file_name}"].insert_many(records)
                else:
                    mongo[f"{DB_NAME}.{file_name}"].insert_one(records)

def find(db_name: str, col_name: str, query: str):
    if db_name and col_name and query:
        return json.loads(json_util.dumps(list(mongo[f"{db_name}.{col_name}"].find(eval(query)))))