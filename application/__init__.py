from flask import Flask
from flask_pymongo import PyMongo
from application import constant

# MongoDB Settings
MONGO_URI = constant.MONGO_URI
DB_NAME = constant.DB_NAME

# Initialize Flask app
app = Flask(__name__)

# MongoDB setup
app.config['DEBUG'] = True
app.config["MONGO_URI"] = MONGO_URI #+ "/analysis"
mongo = PyMongo(app).cx[DB_NAME] # DB_NAME = ’analysis‘
