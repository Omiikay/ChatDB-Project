# constants.py

"""This module defines project-level constants."""

# MongoDB connection URI
EC2_SERVER = "ec2-54-67-105-224.us-west-1.compute.amazonaws.com"
PORT = "27017"
MONGO_URI = f"mongodb://{EC2_SERVER}:{PORT}"
DB_NAME = "analysis"

# Upload File Type
TYPE_CSV = "text/csv"
TYPE_JSON = "application/json"