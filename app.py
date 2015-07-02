from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

STRIPE_KEY = "STRIPE_API_KEY"
AUTHENTISE_KEY = "AUTHENTISE_API_KEY"


app = Flask(__name__)
app.secret_key = 'thisisasecret' #You need to set up an app secret key.


# Set up the SQLAlchemy Database to be a local file 'store.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/store'
db = SQLAlchemy(app)


if __name__ == "__main__":
    from views import *
    app.run(debug=True)
