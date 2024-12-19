# constant.py
'''
File name: constant.py
Function: 
Comment: This module defines project-level constants.
'''

# MongoDB connection URI
EC2_SERVER = "ec2-54-193-37-171.us-west-1.compute.amazonaws.com" # not permanent
PORT = "27017"
MONGO_URI = f"mongodb://{EC2_SERVER}:{PORT}"
DB_NAME = "sns_test"

# Upload File Type
TYPE_CSV = "text/csv"
TYPE_JSON = "application/json"

#Mysql connection config
HOST = "localhost"
USER = "root"
PASSWORD = "12345678"
DATABASE = "test"
CHARSET = 'utf8mb4'

#Sample generation
NUM = 3