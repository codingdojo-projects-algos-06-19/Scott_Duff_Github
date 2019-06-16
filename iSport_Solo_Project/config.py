from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.secret_key = "secretkey"


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_compiler.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


migrate = Migrate(app, db)


bcrypt = Bcrypt(app)
