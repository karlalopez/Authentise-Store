from flask import render_template, request, redirect, session, jsonify, url_for
from models import *
from app import *
from forms import *
from werkzeug import secure_filename
from flask.ext.login import login_user, logout_user, login_required, LoginManager, current_user

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =  "signin"
LOGIN_URL = '/login'

@login_manager.user_loader
def load_user(userid):
    return User.query.filter(User.id==userid).first()

@app.route('/')
def index():
    return render_template('index.html', shop_name=shop_name, shop_tagline=shop_tagline)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        print "form validated"
        # Check for username
        user_login = get_user_by_email(form.email.data)
        if user_login:
            print "user found"
            # Check for password
            if user_login.password == form.password.data:
                print "pass found"
                login_user(user_login)
                return redirect('/shop')
        return render_template('login.html', error="Login credentials don't not work", form=form, shop_name=shop_name, shop_tagline=shop_tagline)
    return render_template('login.html', form=form, shop_name=shop_name, shop_tagline=shop_tagline)


@app.route('/logout')
def logout():
    if current_user.is_authenticated():
        logout_user()
    return redirect('/shop')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Look for session
    if current_user.is_authenticated():
        return redirect('/shop')
    else:
        form = UserForm(request.form)
        if request.method == 'POST' and form.validate():
            # Check for duplicated username
            if get_user_by_email(form.email.data):
                return render_template('signup.html', form=form, shop_name=shop_name, shop_tagline=shop_tagline, error="Email already taken")
            # If no duplicates, create user
            else:
                try:
                    user = create_user(form.email.data, form.password.data)
                    return redirect(url_for('login'))
                except Exception as e:
                    return render_template('signup.html', form=form, shop_name=shop_name, shop_tagline=shop_tagline, error=e.message)
        return render_template('signup.html', shop_name=shop_name, shop_tagline=shop_tagline,form=form)

@app.route('/shop')
def shop():
    collections = get_collections()
    models = get_models()
    return render_template('shop.html', models=models, collections=collections, shop_name=shop_name, shop_tagline=shop_tagline)

@app.route('/shop/popularity')
def shop_pop():
    # Lists the models by popularity
    collections = get_collections()
    models = get_popular_models()
    return render_template('shop.html', models=models, collections=collections, shop_name=shop_name, shop_tagline=shop_tagline)

@app.route('/search', methods=['POST'])
def search():
    collections = get_collections()
    search = request.form.get('term')
    models = search_models(search)
    if models == []:
        return render_template('shop.html', error="Sorry, no matched to your search.", email=email, models=models, collections=collections, shop_name=shop_name, shop_tagline=shop_tagline)
    return render_template('shop.html', models=models, collections=collections, shop_name=shop_name, shop_tagline=shop_tagline)

@app.route('/collection/<id>')
def collection(id):
    collections = get_collections()
    models = get_models_by_collection(id)
    collection_name = get_collection_name_by_id(id)
    return render_template('shop.html', email=email, models=models, collections=collections, collection_name=collection_name)

@app.route('/product/<id>')
def product(id):
    model = get_model_by_id(id)
    if model:
        images = get_images_by_model_id(id)
        error = " "
    else:
        error = "Model does not exist."
        images = " "
    collections = get_collections()
    return render_template('product.html', error=error, model=model, images=images, collections=collections, key=stripe_keys['publishable_key'], shop_name=shop_name, shop_tagline=shop_tagline)

@app.route('/models')
def models():
    # Not a valid route
    return redirect('/shop')


@app.route('/checkout/<id>', methods=['POST'])
def checkout(id):
    # Checks if the user is authenticated
    if current_user.is_authenticated():
        model = get_model_by_id(id)
        collections = get_collections()
        amount = int(model.price * 100)
        images = get_images_by_model_id(id)
        image_path = images[0].path

        # Create customer on Stripe
        customer = stripe.Customer.create(
            email=email,
            card=request.form['stripeToken']
        )
        # Create charge on Stripe
        charge = stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency='usd',
            description='Flask Charge'
        )

        # Create order token on the db
        token = create_token(model.price, model.id, email)

        # If Stripe paid is okay
        if charge.status == 'paid':
            stripe_charge_id = charge.id
            # Update model popularity
            popularity = update_model_popularity(model)
            # Create Authentise token link
            token_link = create_authentise_token(model,token)
            authentise_token, authentise_link = token_link

            # Update order token on the db woth Stripe charge id and Authentise token link
            token = update_token(token, authentise_token, stripe_charge_id)

            # Render interface to print
            return render_template('checkout.html', authentise_link=authentise_link, image_path=image_path, token=token, email=email, collections=collections, shop_name=shop_name, shop_tagline=shop_tagline)
        else:
            error = "We are very sorry, but there was a problem with your purchase. Please try again."
            return render_template('product.html', email=email, model=model, collections=collections, error=error, shop_name=shop_name, shop_tagline=shop_tagline)

    else:
        # If user is not authenticated, render login
        return render_template('login.html')

@app.route('/print/<id>')
def print_order(id):
    # Checks if the user is authenticated
    if current_user.is_authenticated():
        # Get order info
        token = get_token_by_id(id)
        image = get_first_image_by_model_id(token.model_id)
        image_path = image.path
        collections = get_collections()

        # Form the Authentise token link
        authentise_link = "http://app.authentise.com/#/widget/{}".format(token.authentise_token)

        return render_template('checkout.html', image_path=image_path, token=token, authentise_link=authentise_link, collections=collections, shop_name=shop_name, shop_tagline=shop_tagline)
    # If user is not authenticated, render login
    else:
        return render_template('login.html')


@app.route('/profile')
def profile():
    # Checks if the user is authenticated
    if current_user.is_authenticated():
        # Get all orders from this user
        tokens = get_tokens_by_email(current_user.email)
        token_status = []
        for token in tokens:
            s = get_token_print_status(token.authentise_token)
            token_status.append(s)
        return render_template('profile.html', tokens=tokens, token_status=token_status, shop_name=shop_name, shop_tagline=shop_tagline)
    return redirect('/login')

# Admin routes

@app.route('/admin')
def admin():
    # Checks if the user is authenticated & admin
    if current_user.is_authenticated():
        user = get_user_by_email(current_user.email)
        if user.admin == True:
            models = get_10_models()
            tokens = get_10_tokens()
            token_status = get_token_list_status(tokens)
            users = get_10_users()
            return render_template('admin.html', models=models, tokens=tokens, token_status=token_status, users=users, shop_name=shop_name, shop_tagline=shop_tagline)
    # If not authenticated and admin, redirects to shop
    return redirect('/shop')


# Models route

@app.route('/admin-models')
def adminmodels():
    # Checks if the user is authenticated & admin
    if current_user.is_authenticated():
        user = get_user_by_email(current_user.email)
        if user.admin == True:
            models = get_10_models()
            tokens = get_10_tokens()
            users = get_10_users()
            return render_template('admin-models.html', models=models, shop_name=shop_name, shop_tagline=shop_tagline)
    # If not authenticated and admin, redirects to shop
    return redirect('/shop')

@app.route('/admin-models/<id>', methods=['GET', 'POST'])
def adminmodels_view(id):
    # Checks if the user is authenticated & admin
    if current_user.is_authenticated():
        user = get_user_by_email(current_user.email)
        if user.admin == True:
            model = get_model_by_id(id)
            images = get_images_by_model_id(id)
            collections = get_collections()
            # If it's a GET, render template with model info
            if request.method == 'GET':
                return render_template('view-model.html', email=email, model=model, collections=collections, images=images, shop_name=shop_name, shop_tagline=shop_tagline)
            # If POST, use the info to update the model
            model_name = request.form.get('model_name_field')
            model_description = request.form.get('model_description_field')
            model_collection = request.form.get('model_collection_field')
            model_dimensions = request.form.get('model_dimensions_field')
            model_price = request.form.get('model_price_field')
            try:
                # Update model
                model_to_update = update_model(model, model_name, model_description, model_dimensions, model_collection, model_price)
                return redirect('admin-models')
            except Exception as e:
                return render_template('view-model.html', error=e.message, email=email, model=model, collections=collections, images=images, shop_name=shop_name, shop_tagline=shop_tagline)
    # If not authenticated and admin, redirects to shop
    return redirect('/shop')

@app.route('/admin-models/new', methods=['GET', 'POST'])
def adminmodels_new():
    # Checks if the user is authenticated & admin
    if current_user.is_authenticated():
        user = get_user_by_email(current_user.email)
        if user.admin == True:
            # If GET render template to add new model
            if request.method == 'GET':
                return render_template('new-model.html', email=email, collections=collections, shop_name=shop_name, shop_tagline=shop_tagline)

            # If POST, use the info to create a new model
            model_name = request.form.get('model_name_field')
            model_description = request.form.get('model_description_field')
            model_collection = request.form.get('model_collection_field')
            model_dimensions = request.form.get('model_dimensions_field')
            model_price = request.form.get('model_price_field')

            # Get the STL file, save it on the Models dir and put the path to the model on a variable
            file = request.files['model_path_field']
            model_path = save_model(file)

            try:
                # Create the new model
                model_to_create = create_model(model_name, model_path, model_description, model_dimensions, model_collection, model_price)
                # Save images to the Uploads dir and add their paths to the images table on the db
                images = save_images(model_to_create, request.files['model_image1_field'],request.files['model_image2_field'], request.files['model_image3_field'], request.files['model_image4_field'], request.files['model_image5_field'])
            except Exception as e:
                return render_template('new-model.html', error=e.message, email=email, collections=collections, shop_name=shop_name, shop_tagline=shop_tagline)

    # If not authenticated and admin, redirects to shop
    return redirect('/admin-models')

@app.route('/admin-models/deactivate/<id>', methods=['GET', 'POST'])
def adminmodels_deactivate(id):
    # Checks if the user is authenticated & admin
    if current_user.is_authenticated():
        user = get_user_by_email(current_user.email)
        if user.admin == True:
            # Make sure the model exists
            model_to_deactivate = get_model_by_id(id)
            # Deactivate model
            if model_to_deactivate:
                deactivate_model(model_to_deactivate.id)
                return redirect('admin-models')
    # If not authenticated and admin, redirects to shop
    return redirect('/shop')

# Collections route

@app.route('/admin-collections')
def admincollections():
    # Checks if the user is authenticated & admin
    if current_user.is_authenticated():
        user = get_user_by_email(current_user.email)
        if user.admin == True:
            collections = get_collections()
            return render_template('admin-collections.html', email=email, collections=collections, shop_name=shop_name, shop_tagline=shop_tagline)
    # If not authenticated and admin, redirects to shop
    return redirect('/shop')

@app.route('/admin-collections/<id>', methods=['GET', 'POST'])
def admincollections_view(id):
    # Checks if the user is authenticated & admin
    if current_user.is_authenticated():
        user = get_user_by_email(current_user.email)
        if user.admin == True:
            collection = get_collection_by_id(id)
            if request.method == 'GET':
                # If GET, render template with collection info
                return render_template('view-collection.html', email=email, collection=collection, shop_name=shop_name, shop_tagline=shop_tagline)
            # If POST, use the info to update collection
            collection_name = request.form.get('collection_name_field')
            collection_description = request.form.get('collection_description_field')
            try:
                # Update collection
                collection_to_update = update_collection(collection, collection_name, collection_description)
                return redirect('admin-collections')
            except Exception as e:
                return render_template('view-collection.html', error=e.message, email=email, collection=collection, shop_name=shop_name, shop_tagline=shop_tagline)
    # If not authenticated and admin, redirects to shop
    return redirect('/shop')

@app.route('/admin-collections/new', methods=['GET', 'POST'])
def admincollections_new():
    # Checks if the user is authenticated & admin
    if current_user.is_authenticated():
        user = get_user_by_email(current_user.email)
        if user.admin == True:
            # If GET, render the template to add new collections
            if request.method == 'GET':
                return render_template('new-collection.html', shop_name=shop_name, shop_tagline=shop_tagline)

            # If POST, use the info to update model
            collection_name = request.form.get('collection_name_field')
            collection_description = request.form.get('collection_description_field')

            try:
                # Update collection
                collection_to_create = create_collection(collection_name, collection_description)
            except Exception as e:
                return render_template('new-collection.html', error=e.message, shop_name=shop_name, shop_tagline=shop_tagline)
    # If not authenticated and admin, redirects to shop
    return redirect('/admin-collections')


@app.route('/admin-collections/deactivate/<id>', methods=['GET', 'POST'])
def admincollections_deactivate(id):
    # Checks if the user is authenticated & admin
    if current_user.is_authenticated():
        user = get_user_by_email(current_user.email)
        if user.admin == True:
            collection_to_deactivate = get_collection_by_id(id)
            # Make sure the collection exists
            if collection_to_deactivate:
                # Deactivate colletion
                deactivate_collection(collection_to_deactivate.id)
                return redirect('admin-collections')
            return redirect('admin-collections')
    # If not authenticated and admin, redirects to shop
    return redirect('/shop')

# Orders route

@app.route('/admin-orders')
def adminorders():
    # Checks if the user is authenticated & admin
    if current_user.is_authenticated():
        user = get_user_by_email(current_user.email)
        if user.admin == True:
            tokens = get_tokens()
            token_status = get_token_list_status(tokens)
            return render_template('admin-orders.html', shop_name=shop_name, shop_tagline=shop_tagline, tokens=tokens, token_status=token_status)
    # If not authenticated and admin, redirects to shop
    return redirect('/shop')

# Please note there is no route to add new, edit or deactivate order, as they are automaticly created using Stripe and Authentise

@app.route('/admin-order/<id>')
def adminorder_view(id):
    # Checks if the user is authenticated & admin
    if current_user.is_authenticated():
        user = get_user_by_email(current_user.email)
        if user.admin == True:
            # Render template with order info
            token = get_token_by_id(id)
            token_status = get_token_print_status(token.authentise_token)
            return render_template('view-order.html', email=email, token=token, token_status=token_status, shop_name=shop_name, shop_tagline=shop_tagline)
    # If not authenticated and admin, redirects to shop
    return redirect('/shop')


# Users route

@app.route('/admin-users')
def adminusers():
    # Checks if the user is authenticated & admin
    if current_user.is_authenticated():
        user = get_user_by_email(current_user.email)
        if user.admin == True:
            users = get_users()
            return render_template('admin-users.html', email=email, users=users, shop_name=shop_name, shop_tagline=shop_tagline)
    # If not authenticated and admin, redirects to shop
    return redirect('/shop')

@app.route('/admin-users/<id>', methods=['GET', 'POST'])
def adminusers_view(id):
    # Checks if the user is authenticated & admin
    if current_user.is_authenticated():
        user = get_user_by_email(current_user.email)
        if user.admin == True:
            # If GET, render template with user info
            if request.method == 'GET':
                user_to_view = get_user_by_id(id)
                return render_template('view-user.html', email=email, user=user_to_view, shop_name=shop_name, shop_tagline=shop_tagline)
            # If POST, use the info to update user
            user_email = request.form.get('user_email_field')
            user_admin = request.form.get('user_admin_field')
            user_to_update = get_user_by_id(id)
            try:
                # Update user
                user_to_update = update_user(user_to_update, user_email, user_admin)
                return redirect('admin-users')
            except Exception as e:
                return render_template('view-user.html', error=e.message, user=user, shop_name=shop_name, shop_tagline=shop_tagline)
    # If not authenticated and admin, redirects to shop
    return redirect('/shop')

@app.route('/admin-users/new', methods=['GET', 'POST'])
def adminusers_new():
    # Checks if the user is authenticated & admin
    if current_user.is_authenticated():
        user = get_user_by_email(current_user.email)
        if user.admin == True:
            # If GET, render template to create new user
            if request.method == 'GET':
                return render_template('new-user.html', shop_name=shop_name, shop_tagline=shop_tagline)
            # If POST, use the info to create new user
            user_email = request.form.get('user_email_field')
            user_password = request.form.get('user_password_field')
            try:
                # Create user
                user = create_user(user_email, user_password)
                return redirect('admin-users')
            except Exception as e:
                return render_template('new-user.html', error=e.message, shop_name=shop_name, shop_tagline=shop_tagline)
    # If not authenticated and admin, redirects to shop
    return redirect('/shop')


# Please note this is a real DELETE route, no deactivate. Once it's deleted, its DONE.

@app.route('/admin-users/delete/<id>', methods=['GET', 'POST'])
def adminusers_delete(id):
    # Checks if the user is authenticated & admin
    if current_user.is_authenticated():
        user = get_user_by_email(current_user.email)
        # Make sure the user exists
        if user.admin == True:
            # Delete user
            user_to_delete = get_user_by_id(id)
            if user_to_delete:
                delete_user(user_to_delete.id)
                return redirect('admin-users')
    # If not authenticated and admin, redirects to shop
    return redirect('/shop')
