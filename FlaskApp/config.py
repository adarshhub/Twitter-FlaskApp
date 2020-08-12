from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = '@12345678@'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:adarsh@localhost/flaskdb'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)