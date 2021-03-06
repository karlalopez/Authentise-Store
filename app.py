from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
from flask.ext.login import LoginManager
import os
from itsdangerous import URLSafeTimedSerializer


# Enter here your shop name and tagline
shop_name = "Shop name"
shop_tagline = "Best shop tagline ever"

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join('static/uploads')
MODELS_FOLDER = os.path.join('models')

ALLOWED_EXTENSIONS = set(['stl'])

app = Flask(__name__)

app.secret_key = 'SECRET_KEY' # You need to set up an app secret key.
ts = URLSafeTimedSerializer(app.config['SECRET_KEY']) # You need to set up an app secret key.

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MODELS_FOLDER'] = MODELS_FOLDER


# Set up the SQLAlchemy Database to be a local file 'store.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/store'
db = SQLAlchemy(app)


if __name__ == "__main__":
    from views import *
    del session
    app.run(debug=True)
