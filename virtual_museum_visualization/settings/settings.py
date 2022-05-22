# FLASK APP GLOBAL SETTINGS

import os
from datetime import timedelta

from flask import Flask
from flask_restful import Api
from pymongo import MongoClient
from bson import ObjectId

# import secrets
# import bcrypt
# import hashlib


####################################################################
# Get environment variables
###################################################################
# MONGOATLAS = True if os.getenv('MONGOATLAS') == "True" else False
# MONGOATLAS_URI = os.getenv('MONGOATLAS_URI')


CONNECTION_URI = os.getenv("MONGO_CONNECT")

####################################################################
# Flask and Mongo configs
###################################################################

# Configure flask app and flask-restful
ROOT_DIR = os.path.dirname(os.path.abspath("main.py"))
app = Flask(__name__,
            template_folder=os.path.join(ROOT_DIR, "views"),
            static_folder=os.path.join(ROOT_DIR, "static"))
app.config['FLASK_ENV'] = 'development'
app.config['SECRET_KEY'] = "jq=&2d^4GHhz@P$9YA*V"
api = Api(app)

# Set session lifetime
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

client = MongoClient(CONNECTION_URI, connect=False)
db = client.virtualmuseum
Users = db['users']

# MESA server
mesa_manager_api_endpoint = "http://virtualmuseum_manager:8521/api/v1"
