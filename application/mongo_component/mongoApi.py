from typing import Any, Dict, List
from application import mongo, constant, DB_NAME
from bson import json_util
import json
import pandas as pd

# def save_upload(inputFile: dict):
def save_upload(inputFile, df: pd.DataFrame):
    # Loading or Opening the json file
    if inputFile:
        file_name = inputFile.filename.split('.')[0]
        match (inputFile.content_type):
            case constant.TYPE_JSON:
                records = [json.loads(line) for line in inputFile]
                if len(records) > 1:
                    # mongo.db[inputJson.filename].insert_many(inputJson)
                    mongo[f"{DB_NAME}.{file_name}"].insert_many(records)
                else:
                    # mongo.db[inputJson.filename].insert_one(inputJson)
                    mongo[f"{DB_NAME}.{file_name}"].insert_one(records)
            case constant.TYPE_CSV:
                # convert csv to dict records format by pandas
                records = df.to_dict('records')
                if len(records) > 1:
                    mongo[f"{DB_NAME}.{file_name}"].insert_many(records)
                else:
                    mongo[f"{DB_NAME}.{file_name}"].insert_one(records)           

def find(col_name: str, filter: dict, projection: dict = None, db_name: str = DB_NAME):
    if db_name and col_name and filter:
        return json.dumps(json.loads(json_util.dumps(list(mongo[f"{db_name}.{col_name}"].find(filter, projection)))), indent=2)  
    

def aggregate(col_name: str, pipeline: List[Dict[str, Any]], db_name:  str = DB_NAME):
    if db_name and col_name:
        return json.dumps(json.loads(json_util.dumps(list(mongo[f"{db_name}.{col_name}"].aggregate(pipeline)))), indent=2)  
    

def find_all(col_name: str, db_name: str = DB_NAME):
    if db_name and col_name:
        json_str = json_util.dumps(list(mongo[f"{db_name}.{col_name}"].find().limit(5)))
        return json.dumps(json.loads(json_str), indent=2)