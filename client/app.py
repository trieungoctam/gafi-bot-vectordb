from flask import Flask
from flask_cors import CORS

app = Flask(__name__, template_folder="./html")
CORS(app, resources={r"*": {"origins": "*"}})