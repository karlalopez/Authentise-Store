from app import db, ALLOWED_EXTENSIONS
import datetime
import os
from werkzeug import secure_filename
from app import app


class Collection(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))

    def __init__(self, name, description):
        self.name = name
        self.description = description

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
        self.date_added = date_added
        self.collection_id = collection_id
        self.popularity = 0
        self.active = True


class Image(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(200))
    model_id = db.Column(db.Integer, db.ForeignKey('model.id'))
    # model = db.relationship("Model", backref="images")

    def __init__(self, path, model_id):
        self.path = path
        self.model_id = model_id


class Token(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100))
    date_added = db.Column(db.Date)
    price_paid = db.Column(db.Float)
    stripe_charge_id = db.Column(db.String(100))
    model_id = db.Column(db.Integer, db.ForeignKey('model.id'))
    model = db.relationship("Model", backref="token")
    user_email = db.Column(db.String(100), db.ForeignKey('user.email'))
    user = db.relationship("User", backref="token")

    def __init__(self, date_added, price_paid, model_id, user_email, stripe_charge_id=None):
        self.date_added = date_added
        self.price_paid = price_paid
        self.model_id = model_id
        self.user_email = user_email

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100),unique=True)
    date_added = db.Column(db.Date)
    password = db.Column(db.String(100))
    admin = db.Column(db.Boolean)

    def __init__(self, email, date_added, password, admin):
        self.email = email
        self.date_added = date_added
        self.password = password
        self.admin = admin


# User related functions

def get_users():
    users = User.query.all()
    return users


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

def get_user_by_id(id):
    return User.query.filter_by(id=id).first()


def create_user(email, password, admin): # Try?
    print User.query.count()
    if User.query.count() == 0:
        admin = True
        date_added = datetime.date.today()
        user = User(email, date_added, password, admin)
        db.session.add(user)
        db.session.commit()
        return user
    else:
        date_added = datetime.date.today()
        user = User(email, date_added, password, admin)
        db.session.add(user)
        db.session.commit()
        return user

def update_user(user, user_email, user_admin):
    if user_email is None or user_email == '':
        raise Exception("User needs a valid email")

    user.email = user_email
    user.admin = user_admin
    try:
        db.session.commit()
        return user
    except:
        # If something went wrong, explicitly roll back the database
        db.session.rollback()


def delete_user(id):
    user = User.query.get(id)
    if user:
        email = user.email
        db.session.delete(user)

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
    models = Model.query.filter_by(active='True').all()
    return models

def get_model_by_id(id):
    return Model.query.filter_by(id=id).first()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def save_model(file):
    filename = "{}{}".format(datetime.datetime.today(),secure_filename(file.filename))
    print filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    model_path = "/{}/{}".format(app.config['UPLOAD_FOLDER'], filename)
    return model_path

def create_model(model_name, model_path, model_description, model_dimensions, model_collection, model_price):

    date_added = datetime.date.today()
    model = Model(model_name, model_path, model_description, model_dimensions, model_price, date_added, model_collection)

    try:
        db.session.add(model)
        print "db.add"
        db.session.commit()
        print "db.commit"
        return model
    except Exception as e:
        db.session.rollback()
        print e
        return e

def update_model(model, model_name, model_description, model_dimensions, model_collection, model_price):
    # if user_email is None or user_email == '':
    #     raise Exception("Model needs a valid info")
    print "Model update"
    model.name = model_name
    model.description = model_description
    model.dimensions = model_dimensions
    model.collection_id = model_collection
    print model_collection
    model.price = model_price
    print model.price
    try:
        db.session.commit()
        return model
    except:
        # If something went wrong, explicitly roll back the database
        db.session.rollback()


def deactivate_model(id):
    model = Model.query.get(id)
    if model:
        print "Model deactivation"
        model.active = False
        try:
            db.session.commit()
            return model
        except:
            # If something went wrong, explicitly roll back the database
            db.session.rollback()

# Images related functions

def get_images_by_model_id(id):
    return Image.query.filter_by(model_id=id).all()

def add_images_to_model(path, model_id):
    image = Image(path, model_id)

    try:
        db.session.add(image)
        print "db.add"
        db.session.commit()
        print "db.commit"
        return image
    except Exception as e:
        db.session.rollback()
        print e
        return e

def save_images(model_to_create, model_image1, model_image2, model_image3, model_image4, model_image5):

    model_id = model_to_create.id

    images = [model_image1, model_image2, model_image3, model_image4, model_image5]

    for image in images:
        if image != None or image != "":
            filename = "{}{}".format(datetime.datetime.today(),secure_filename(image.filename))
            print filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            image_path = "/{}/{}".format(app.config['UPLOAD_FOLDER'], filename)
            try:
                save_image = add_images_to_model(image_path, model_id)
            except Exception as e:
                db.session.rollback()
                print e
                return e



# Collection related functions

def get_collections():
    collections = Collection.query.all()
    for collection in collections:
        print collection.name
    return collections


if __name__ == "__main__":

    # Run this file directly to create the database tables.
    print "Creating database tables..."
    db.create_all()
    print "Done!"
