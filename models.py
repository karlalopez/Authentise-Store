from app import db
import datetime

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
    path = db.Column(db.String(100))
    description = db.Column(db.String(255))
    dimensions = db.Column(db.String(100))
    price = db.Column(db.Float)
    date_added = db.Column(db.Date)
    popularity = db.Column(db.Integer)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'))
    collection = db.relationship("Collection", backref="models")

    def __init__(self, name, path, description, dimensions, price, date_added, popularity, collection_id):
        self.name = name
        self.path = path
        self.description = description
        self.dimensions = dimensions
        self.price = price
        self.date_added = date_added
        self.popularity = popularity
        self.collection_id = collection_id

class Image(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(100))
    model_id = db.Column(db.Integer, db.ForeignKey('model.id'))
    model = db.relationship("Model", backref="images")

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
    models = Model.query.all()
    return model


def get_model_by_id(id):
    return Model.query.filter_by(id=id).first()

# def create_model(----):
#     date_added = datetime.date.today()
#     #####
#     model = Model(-----)
#     db.session.add(model)
#     try:
#         db.session.commit()
#         return model
#     except:
#         db.session.rollback()
#         return False
#
# def update_model(----):
#     if user_email is None or user_email == '':
#         raise Exception("Model needs a valid info")
#
#     #####
#     try:
#         db.session.commit()
#         return user
#     except:
#         # If something went wrong, explicitly roll back the database
#         db.session.rollback()


def delete_user(id):
    model = Model.query.get(id)
    if model:
        db.session.delete(model)

        try:
            db.session.commit()
            return "Model {} deleted".format(id)
        except:
            # If something went wrong, explicitly roll back the database
            db.session.rollback()
            return "Something went wrong"
    else:
            return "Model not found"

# Images related functions

def get_images_by_model_id(id):
    return Image.query.filter_by(model_id=id).all()


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
