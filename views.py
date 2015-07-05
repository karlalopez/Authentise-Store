from flask import render_template, request, redirect, session, jsonify, url_for
from models import *
from app import *
from werkzeug import secure_filename

@app.route('/')
def index():
    return render_template('index.html', shop_name=shop_name, shop_tagline=shop_tagline)

@app.route('/login')
def login():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        return redirect('/shop')
    else:
        return render_template('/login.html')

@app.route('/submit-login', methods=['POST'])
def submit_login():
    user_email = request.form.get('email_field')
    user_password = request.form.get('password_field')

    # check for username
    user_login = get_user_by_email(user_email)
    if user_login:
        if user_login.password == user_password:
            session['email'] = user_email
            return redirect('/shop')
        else:
            return render_template('login.html', error="Login credentials don't not work")
    else:
        return render_template('login.html', error="Login credentials don't not work")

@app.route('/logout')
def logout():
    if session.get('email'):
        email = session['email']
        del session['email']
    return redirect('/shop')

@app.route('/signup')
def signup():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        return redirect('/shop')
    else:
        return render_template('signup.html')

@app.route('/submit-signup', methods=['POST'])
def submit_signup():
    #get form info
    user_email = request.form.get('email_field')
    user_password = request.form.get('password_field')
    print user_email

    # check for duplicated username
    if get_user_by_email(user_email):
        return render_template('signup.html',error="Email already taken")
    # if no duplicates, create user
    else:
        try:
            user = create_user(user_email, user_password)
            print user
            session['email'] = user_email
            return redirect('/shop')
        except Exception as e:
            # Oh no, something went wrong!
            # We can access the error message via e.message:
            return render_template('signup.html', error=e.message)

@app.route('/shop')
def shop():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        collections = get_collections()
        models = get_models()
        return render_template('shop.html', email=email, models=models, collections=collections)
    else:
        collections = get_collections()
        models = get_models()
        return render_template('shop.html')

@app.route('/product/<id>')
def product(id):
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        model = get_model_by_id(id)
        if model:
            images = get_images_by_model_id(id)
            error = " "
        else:
            error = "Model does not exist."
            images = " "
        collections = get_collections()
        return render_template('product.html', error=error, email=email, model=model, images=images, collections=collections, key=stripe_keys['publishable_key'])
    else:
        model = get_model_by_id(id)
        images = get_images_by_model_id(id)
        collections = get_collections()
        return render_template('product.html', model=model, images=images, collections=collections, key=stripe_keys['publishable_key'])

@app.route('/checkout/<id>', methods=['POST'])
def checkout(id):
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        model = get_model_by_id(id)
        collections = get_collections()
        # create authentise token
        authentise_token = "045234rfjwkeh83453rf"
        new_token = create_token(authentise_token, model.price, model.id, email)
        amount = int(model.price * 100)

        customer = stripe.Customer.create(
            email=email,
            card=request.form['stripeToken']
        )

        charge = stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency='usd',
            description='Flask Charge'
        )
        if charge.status == 'succeeded':
            stripe_charge_id = charge.id
            token = update_token(new_token, stripe_charge_id)
            return render_template('checkout.html', amount=amount, token=token, email=email, model=model, collections=collections)
        else:
            error = "We are very sorry, but there was a problem with your purchase. Please try again."
            return render_template('product.html', email=email, model=model, collections=collections, error=error)

    else:
        return render_template('login.html')


@app.route('/collection/<id>')
def collection(id):
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        collections = get_collections()
        models = get_models_by_collection(id)
        collection_name = get_collection_name_by_id(id)
        return render_template('shop.html', email=email, models=models, collections=collections, collection_name=collection_name)
    else:
        collections = get_collections()
        models = get_models_by_collection(id)
        collection_id = id
        return render_template('shop.html', models=models, collections=collections, collection_id=collection_id)


@app.route('/admin')
def admin():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            return render_template('admin.html', email=email)
    return redirect('/shop')


# Models route

@app.route('/admin-models')
def adminmodels():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        models = get_models()
        if user.admin == True:
            return render_template('admin-models.html', models=models,email=email)
    return redirect('/shop')

@app.route('/admin-models/<id>', methods=['GET', 'POST'])
def adminmodels_view(id):
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            model = get_model_by_id(id)
            images = get_images_by_model_id(id)
            collections = get_collections()
            if request.method == 'GET':
                print "get"
                return render_template('view-model.html', email=email, model=model, collections=collections, images=images)
            print "post"
            model_name = request.form.get('model_name_field')
            model_description = request.form.get('model_description_field')
            model_collection = request.form.get('model_collection_field')
            model_dimensions = request.form.get('model_dimensions_field')
            model_price = request.form.get('model_price_field')
            try:
                model_to_update = update_model(model, model_name, model_description, model_dimensions, model_collection, model_price)
                print model_to_update
                return redirect('admin-models')
            except Exception as e:
                return render_template('view-model.html', error=e.message, email=email, model=model, collections=collections, images=images)

    return redirect('/shop')

@app.route('/admin-models/new', methods=['GET', 'POST'])
def adminmodels_new():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        collections = get_collections()
        if user.admin == True:
            if request.method == 'GET':
                print "get"
                return render_template('new-model.html', email=email, collections=collections)

            print "post"
            model_name = request.form.get('model_name_field')
            model_description = request.form.get('model_description_field')
            model_collection = request.form.get('model_collection_field')
            model_dimensions = request.form.get('model_dimensions_field')
            model_price = request.form.get('model_price_field')

            file = request.files['model_path_field']
            model_path = save_model(file)
            print "model path: {}".format(model_path)

            try:
                model_to_create = create_model(model_name, model_path, model_description, model_dimensions, model_collection, model_price)
                images = save_images(model_to_create, request.files['model_image1_field'],request.files['model_image2_field'], request.files['model_image3_field'], request.files['model_image4_field'], request.files['model_image5_field'])
            except Exception as e:
                return render_template('new-model.html', error=e.message, email=email, collections=collections)

    return redirect('/admin-models')

@app.route('/admin-models/deactivate/<id>', methods=['GET', 'POST'])
def adminmodels_deactivate(id):
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            model_to_deactivate = get_model_by_id(id)
            if model_to_deactivate:
                deactivate_model(model_to_deactivate.id)
                return redirect('admin-models')
    return redirect('/shop')

# Collections route

@app.route('/admin-collections')
def admincollections():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            collections = get_collections()
            return render_template('admin-collections.html', email=email, collections=collections)
    return redirect('/shop')

@app.route('/admin-collections/<id>', methods=['GET', 'POST'])
def admincollections_view(id):
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            collection = get_collection_by_id(id)
            if request.method == 'GET':
                print "get"
                return render_template('view-collection.html', email=email, collection=collection)
            print "post"
            collection_name = request.form.get('collection_name_field')
            collection_description = request.form.get('collection_description_field')
            try:
                collection_to_update = update_collection(collection, collection_name, collection_description)
                print collection_to_update
                return redirect('admin-collections')
            except Exception as e:
                return render_template('view-collection.html', error=e.message, email=email, collection=collection)

    return redirect('/shop')

@app.route('/admin-collections/new', methods=['GET', 'POST'])
def admincollections_new():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            if request.method == 'GET':
                print "get"
                return render_template('new-collection.html', email=email)

            print "post"
            collection_name = request.form.get('collection_name_field')
            print collection_name
            collection_description = request.form.get('collection_description_field')
            print collection_description
            try:
                print "try"
                collection_to_create = create_collection(collection_name, collection_description)
            except Exception as e:
                return render_template('new-collection.html', error=e.message, email=email)
    return redirect('/admin-collections')


@app.route('/admin-collections/deactivate/<id>', methods=['GET', 'POST'])
def admincollections_deactivate(id):
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            collection_to_deactivate = get_collection_by_id(id)
            if collection_to_deactivate:
                print collection_to_deactivate.id
                deactivate_collection(collection_to_deactivate.id)
                return redirect('admin-collections')
            return render_template('admin-collections.html', email=email)
    return redirect('/shop')

# Orders route

@app.route('/admin-orders')
def adminorders():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            # delete function
            return render_template('admin-orders.html', email=email)
    return redirect('/shop')

@app.route('/admin-order/<id>', methods=['GET', 'POST'])
def adminorder_view(id):
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            return render_template('view-orders.html', email=email)
    return redirect('/shop')

@app.route('/admin-order/delete/<id>', methods=['GET', 'POST'])
def adminorders_delete(id):
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            # delete function
            return render_template('admin-orders', email=email)
    return redirect('/shop')

# Users route

@app.route('/admin-users')
def adminusers():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            users = get_users()
            return render_template('admin-users.html', email=email, users=users)
    return redirect('/shop')

@app.route('/admin-users/<id>', methods=['GET', 'POST'])
def adminusers_view(id):
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            if request.method == 'GET':
                print "get"
                user_to_view = get_user_by_id(id)
                return render_template('view-user.html', email=email, user=user_to_view)
            print "post"
            user_email = request.form.get('user_email_field')
            user_admin = request.form.get('user_admin_field')
            user_to_update = get_user_by_id(id)
            print "user_to_update: {}".format(user_to_update)
            try:
                user_to_update = update_user(user_to_update, user_email, user_admin)
                return redirect('admin-users')
            except Exception as e:
                return render_template('view-user.html', error=e.message, user=user, email=email)

    return redirect('/shop')

@app.route('/admin-users/new', methods=['GET', 'POST'])
def adminusers_new():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            if request.method == 'GET':
                return render_template('new-user.html', email=email)
            user_email = request.form.get('user_email_field')
            user_password = request.form.get('user_password_field')
            try:
                user = create_user(user_email, user_password)
                print user
                return redirect('admin-users')
            except Exception as e:
                return render_template('new-user.html', error=e.message, email=email)
    return redirect('/shop')

@app.route('/admin-users/delete/<id>', methods=['GET', 'POST'])
def adminusers_delete(id):
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            user_to_delete = get_user_by_id(id)
            if user_to_delete:
                delete_user(user_to_delete.id)
                return redirect('admin-users')
    return redirect('/shop')

@app.route('/profile')
def profile():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            return render_template('profile.html', email=email)
    return redirect('/login')
