from flask import Flask
from flask_pymongo import PyMongo
from flask_pymysql import MySQL
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

pymysql_kwargs = {
    "host": constant.HOST,
    "user": constant.USER,
    "password": constant.PASSWORD,
    "database": constant.DATABASE,
    "charset": constant.CHARSET,
}

app.config['pymysql_kwargs'] = pymysql_kwargs

mysql = MySQL(app)