from app import app, db, ALLOWED_EXTENSIONS
from flask.ext.bcrypt import Bcrypt
from werkzeug import secure_filename
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy.ext.hybrid import hybrid_property
from flask.ext.login import UserMixin

# import argparse
import datetime
import json
import os
import requests
import time
import stripe

bcrypt = Bcrypt(app)
BCRYPT_LOG_ROUNDS = 12

stripe_keys = {
    'secret_key': os.environ['STRIPE_SECRET_KEY'],
    'publishable_key': os.environ['STRIPE_PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

AUTHENTISE_KEY = os.environ['AUTHENTISE_API_KEY']

MAILGUN_API_KEY = os.environ['MAILGUN_API_KEY']

MAILGUN_SANDBOX_DOMAIN_URL = os.environ['MAILGUN_SANDBOX_DOMAIN_URL']


today = datetime.datetime.today()
todayiso = today.isoformat()

# DB Models

class Collection(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))
    active = db.Column(db.Boolean)

    def __init__(self, name, description,active=None):
        self.name = name
        self.description = description
        self.active = True


class Model(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    path = db.Column(db.String(200))
    description = db.Column(db.String(255))
    dimensions = db.Column(db.String(100))
    price = db.Column(db.Float)
    date_added = db.Column(db.Date)
    popularity = db.Column(db.Integer)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'))
    collection = db.relationship("Collection", backref="models")
    active = db.Column(db.Boolean)

    def __init__(self, name, path, description, dimensions, price, date_added, collection_id,popularity=None,active=None):
        self.name = name
        self.path = path
        self.description = description
        self.dimensions = dimensions
        self.price = price
        self.date_added = today
        self.collection_id = collection_id
        self.popularity = 0
        self.active = True


class Image(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(200))
    model_id = db.Column(db.Integer, db.ForeignKey('model.id'))
    model = db.relationship("Model", backref="images")

    def __init__(self, path, model_id):
        self.path = path
        self.model_id = model_id


class Token(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    authentise_token = db.Column(db.String(100))
    date_added = db.Column(db.Date)
    price_paid = db.Column(db.Float)
    stripe_charge_id = db.Column(db.String(100))
    model_id = db.Column(db.Integer, db.ForeignKey('model.id'))
    model = db.relationship("Model", backref="token")
    user_email = db.Column(db.String(100), db.ForeignKey('user.email'))
    user = db.relationship("User", backref="token")

    def __init__(self,date_added, price_paid, model_id, user_email, authentise_token=None, stripe_charge_id=None):
        self.date_added = today
        self.price_paid = price_paid
        self.model_id = model_id
        self.user_email = user_email

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100),unique=True)
    date_added = db.Column(db.Date)
    _password = db.Column(db.String(100))
    admin = db.Column(db.Boolean)
    email_confirmed = db.Column(db.Boolean)

    def __init__(self, email, date_added, password, admin, email_confirmed=None):
        self.email = email
        self.date_added = today
        self.password = password
        self.admin = admin
        self.email_confirmed = False 

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def is_correct_password(self, plaintext):
        return bcrypt.check_password_hash(self._password, plaintext)


# User related functions

def get_users():
    # Get all users
    users = User.query.all()
    return users

def get_10_users():
    # Get last 10 users created
    users = User.query.limit(10)
    return users

def get_user_by_email(email):
    # Get user by email
    return User.query.filter_by(email=email).first()

def get_user_by_id(id):
    # Get user by user id
    return User.query.filter_by(id=id).first()

def create_user(email, password):
    # Create user
    # If it's the first user in the DB, it becomes admin.
    if User.query.count() == 0:
        admin = True
        date_added = today
        user = User(email, date_added, password, admin)
        db.session.add(user)
        db.session.commit()
        return user
    else:
        # If it's not, then it's not admin
        date_added = today
        admin = False
        user = User(email, date_added, password, admin)
        db.session.add(user)
        db.session.commit()
        return user

def send_email_to_user(email, subject, html, shop_name):
    mailgun_url = "https://api.mailgun.net/v3/{}/messages".format(MAILGUN_SANDBOX_DOMAIN_URL)
    from_shop_name = "{} <mailgun@{}>".format(shop_name, MAILGUN_SANDBOX_DOMAIN_URL)
    return requests.post(
        mailgun_url,
        auth=("api", MAILGUN_API_KEY),
        data={"from": from_shop_name,
              "to": [email, "klo.lopez@gmail.com"],
              "subject": subject,
              "text": html})

def confirm_user(email):
    # Marks the user as confirmed on the db
    user = get_user_by_email(email)
    if user:

        user.email_confirmed = True
        try:
            db.session.add(user)
            db.session.commit()
            return user
        except:
            # If something went wrong, explicitly roll back the database
            db.session.rollback()

def update_user(user, user_email, user_admin):
    # Update user info
    if user_email is None or user_email == '':
        raise Exception("Invalid user email")
    user.email = user_email
    user.admin = user_admin
    try:
        db.session.commit()
        return user
    except:
        # If something went wrong, explicitly roll back the database
        db.session.rollback()

def change_user_password(user, user_password):
    # Changes user password
    user.password = user_password
    try:
        db.session.commit()
        return user
    except:
        # If something went wrong, explicitly roll back the database
        db.session.rollback()
        return False


def delete_user(id):
    # Delete user
    # Checks if the user exists
    user = User.query.get(id)
    if user:
        email = user.email
        db.session.delete(user)
        # Deletes user
        try:
            db.session.commit()
            return "User {} deleted".format(email)
        except:
            # If something went wrong, explicitly roll back the database
            db.session.rollback()
            return "Something went wrong"
    else:
            return "User not found"


# Model related functions

def get_models():
    # Get all models
    models = Model.query.filter_by(active='True').all()
    return models

def get_10_models():
    # Get lastest 10 models created
    models = Model.query.filter_by(active='True').limit(10)
    return models

def get_popular_models():
    # Get models ordered by field
    models = Model.query.order_by('popularity').all()
    return models

def get_models_by_collection(id):
    # Get model from a collection
    models = Model.query.filter_by(collection_id=id,active='True').all()
    return models

def get_model_by_id(id):
    # Get model by id
    return Model.query.filter_by(id=id).first()

def search_models(search):
    # Search models
    term = '%{}%'.format(search)
    name_models = Model.query.filter(Model.name.match(term))
    description_models = Model.query.filter(Model.description.match(term))
    models = []
    for model in name_models:
        models.append(model)
    for model in description_models:
        if model not in models:
            models.append(model)
    return models

def create_model(model_name, model_path, model_description, model_dimensions, model_collection, model_price):
    # Create a new model
    date_added = today
    model = Model(model_name, model_path, model_description, model_dimensions, model_price, date_added, model_collection)

    try:
        db.session.add(model)
        LOGGER.info("db.add")
        db.session.commit()
        LOGGER.info("db.commit")
        return model
    except Exception as e:
        db.session.rollback()
        LOGGER.info(e)
        return e

def update_model(model, model_name, model_description, model_dimensions, model_collection, model_price):
    # Update a model
    model.name = model_name
    model.description = model_description
    model.dimensions = model_dimensions
    model.collection_id = model_collection
    model.price = model_price

    try:
        db.session.commit()
        return model
    except:
        # If something went wrong, explicitly roll back the database
        db.session.rollback()

def update_model_popularity(model):
    # Update the popularity of a model
    model.popularity += 1
    try:
        db.session.commit()
        return model
    except:
        db.session.rollback()

def deactivate_model(id):
    # Deactivate a model
    model = Model.query.get(id)
    if model:
        LOGGER.info("Model deactivation")
        model.active = False
        try:
            db.session.commit()
            return model
        except:
            # If something went wrong, explicitly roll back the database
            db.session.rollback()

# Saving model STL file related functions

def allowed_file(filename):
    # Check if the file has a valid name
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def save_model(file):
    # Save the model on the server
    filename = "{}{}".format(todayiso,secure_filename(file.filename))
    file.save(os.path.join(app.config['MODELS_FOLDER'], filename))
    # Return the path to the model in the server
    model_path = "/{}/{}".format(app.config['MODELS_FOLDER'], filename)
    return model_path

# Saving images files related functions

def get_images_by_model_id(id):
    # Get all images of a model by model id
    return Image.query.filter_by(model_id=id).all()

def get_first_image_by_model_id(id):
    # Get one image of a model by model id
    return Image.query.filter_by(model_id=id).first()

def save_images(model_to_create, model_image1, model_image2, model_image3, model_image4, model_image5):
    # Save an images on the server and creates an entries for them on the DB
    model_id = model_to_create.id
    images = [model_image1, model_image2, model_image3, model_image4, model_image5]

    for image in images:
        if image != None or image != "":
            # If image is not null, save it in the server
            filename = "{}{}".format(todayiso,secure_filename(image.filename))
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Form the image path
            image_path = "/{}/{}".format(app.config['UPLOAD_FOLDER'], filename)
            try:
                # Save image_path on the DB
                save_image = add_images_to_model(image_path, model_id)
            except Exception as e:
                db.session.rollback()
                LOGGER.info(e)
                return e

def add_images_to_model(path, model_id):
    # Save image_path on the DB, binding it to a model by model id
    image = Image(path, model_id)

    try:
        db.session.add(image)
        db.session.commit()
        return image
    except Exception as e:
        db.session.rollback()
        return e


# Collection related functions

def get_collections():
    # Get all collections
    collections = Collection.query.filter_by(active='True').all()
    return collections

def get_collection_name_by_id(id):
    # Get a collection name by id
    collection = Collection.query.filter_by(id=id).first()
    return collection.name

def get_collection_by_id(id):
    # Get collection by id
    collection = Collection.query.filter_by(id=id).first()
    return collection

def create_collection(collection_name, collection_description):
    # Create a collection
    collection = Collection(collection_name, collection_description)

    try:
        db.session.add(collection)
        db.session.commit()
        return collection
    except Exception as e:
        db.session.rollback()
        return e

def update_collection(collection, collection_name, collection_description):
    # Update a collection
    collection.description = collection_description

    try:
        db.session.commit()
        return collection
    except Exception as e:
        db.session.rollback()
        return e


def deactivate_collection(id):
    # Deactivate a collection by id
    collection = Collection.query.get(id)
    if collection:
        collection.active = False

        try:
            db.session.commit()
            return collection
        except Exception as e:
            db.session.rollback()
            return e


# Token related functions

def get_tokens():
    # Get all tokens
    tokens = Token.query.order_by(Token.date_added).all()
    return tokens

def get_10_tokens():
    # Get latest 10 tokens created
    tokens = Token.query.order_by(Token.date_added).limit(10)
    return tokens

def get_tokens_by_email(user_email):
    # Get tokens by user email
    tokens = Token.query.filter_by(user_email=user_email).order_by(Token.date_added).all()
    return tokens

def get_token_by_id(id):
    # Get a token by id
    token = Token.query.filter_by(id=id).order_by(Token.date_added).first()
    return token

def create_token(price_paid, model_id, user_email):
    # Create a token
    date_added = today
    token = Token(date_added, price_paid, model_id, user_email)

    try:
        db.session.add(token)
        db.session.commit()
        return token
    except Exception as e:
        db.session.rollback()
        return e

def update_token(token, authentise_token, stripe_charge_id):
    # Update a token
    token.authentise_token = authentise_token
    token.stripe_charge_id = stripe_charge_id

    try:
        db.session.commit()
        return token
    except Exception as e:
        db.session.rollback()
        return e

# Authentise related functions

def authentise_create_token():
    # Authenticate with authentise and create token
    url = 'https://print.authentise.com/api3/api_create_partner_token'
    response = requests.get(url, data={'api_key': AUTHENTISE_KEY})

    if not response.ok:
        raise Exception("Failed to create token: {} {}".format(response.status_code, response.text))
    return response.json()

def authentise_upload_stl(file_name, token_authentise, print_value, email):
    # Upload model STL file to Authentise
    payload = {
        'api_key'               : AUTHENTISE_KEY,
        'token'                 : token_authentise,
        'receiver_email'        : email,
        'print_value'           : print_value,
        'print_value_currency'  : 'USD',
    }
    url = 'https://print.authentise.com/api3/api_upload_partner_stl'
    with open(file_name, 'rb') as f:
        response = requests.post(url, data=payload, files={'stl_file': f})
    if not response.ok:
        raise Exception("Failed to upload {} to token {}: {} {}".format(file_name, token_authentise, response.status_code, response.text))
    return response.json()


def create_authentise_token(model,token):
    # Main Authentise function. Calls authentise_create_token() and authentise_upload_stl
    ROOT = 'authentise.com'

    result = authentise_create_token()
    authentise_token = result['data']['token']

    print_value = token.price_paid  # price of the purchased 3D file
    email = token.user_email    # customer email
    file_name = '.{}'.format(model.path) # customer purchased 3D file

    result = authentise_upload_stl(file_name, authentise_token, print_value, email)
    authentise_token_link = result['data']['ssl_token_link']

    return authentise_token, authentise_token_link

def get_token_print_status(authentise_token):
    # Check the status of a token
    url = "https://print.authentise.com/api3/api_get_partner_print_status?api_key={}&token={}".format(AUTHENTISE_KEY, authentise_token)

    # Parse json output
    authentise_request = requests.get(url)
    resp = json.loads(authentise_request.text)
    if 'data' not in resp:
        status = False
    else:
        if resp[u'data'][u'printing_job_status_name'] == 'SUCCESS':
            status = True
        else:
            status = False

    return status

def get_token_list_status(tokens):
    # Check the status of list of tokens
    token_status = []
    for token in tokens:
        status = get_token_print_status(token.authentise_token)
        token_status.append(status)
    return token_status


if __name__ == "__main__":
    # Run this file directly to create the database tables.
    print "Creating database tables..."
    db.create_all()
    print "Done!"
