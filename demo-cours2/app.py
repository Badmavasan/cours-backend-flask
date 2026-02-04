"""
Flask API with CRUD for User and Todo models.
"""

from flask_migrate import Migrate
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from models import db, User, Todo
from dotenv import load_dotenv
import os


load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]

app = Flask(__name__)

# MySQL connection config
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)


if __name__ == '__main__':
    app.run(debug=True)
