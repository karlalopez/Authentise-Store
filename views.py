from flask import render_template, request, redirect, session, jsonify
from models import *
from app import app

@app.route('/')
def index():
    return render_template('index.html')

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
        return render_template('shop.html', email=email)
    else:
        return render_template('shop.html')
@app.route('/product')
def product():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        return render_template('product.html', email=email)
    else:
        return render_template('product.html')


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
        if user.admin == True:
            return render_template('admin-models.html', email=email)
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
            return render_template('view-model.html', email=email, model=model, collections=collections, images=images)
    return redirect('/shop')

@app.route('/admin-models/new')
def adminmodels_new():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            return render_template('new-model.html', email=email)
    return redirect('/shop')

@app.route('/admin-models/add')
def adminmodels_add():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            # add function
            return render_template('admin-models.html', email=email)
    return redirect('/shop')

@app.route('/admin-models/delete/<id>', methods=['GET', 'POST'])
def adminmodels_delete(id):
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            # delete function
            return render_template('admin-models.html', email=email)
    return redirect('/shop')

# Collections route

@app.route('/admin-collections')
def admincollections():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            # delete function
            return render_template('admin-collections.html', email=email)
    return redirect('/shop')

@app.route('/admin-collections/<id>', methods=['GET', 'POST'])
def admincollections_view(id):
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            # delete function
            return render_template('view-collection.html', email=email)
    return redirect('/shop')

@app.route('/admin-collections/new')
def admincollections_new():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            return render_template('new-collection.html', email=email)
    return redirect('/shop')

@app.route('/admin-collections/add')
def admincollections_add():
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            # add function
            return render_template('admin-collections.html', email=email)
    return redirect('/shop')

@app.route('/admin-collections/delete/<id>', methods=['GET', 'POST'])
def admincollections_delete(id):
    if session.get('email'):
        print "Logged-in: Found session"
        email = session['email']
        user = get_user_by_email(email)
        if user.admin == True:
            # delete function
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
            user_admin = request.form.get('user_admin_field')

            try:
                user = create_user(user_email, user_password, user_admin)
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
