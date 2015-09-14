# Authentise-Store

This is an example of very simple example of an e-commerce website to sell designs for 3D printing using Authentise design streaming.

It's a work in progress, has a lot of restrictions and is meant to be a starting point for people building their own stores.

In addition to Authentise, the services used are: Stripe, Mailgun, and Heroku.

Learn more about Authentise design streaming at http://authentise.com/tech.

Please leave your comments and suggestions. Feedback and pull requests are very welcome.

Special thanks to Jennie Lees. Most of this code was written under her watch and pretty much all this wonderful step-by-step tutorial has been written by her. Visit her portfolio: http://jennielees.github.io.

# Running locally

First, get it ready to run locally:

- Signup for Stripe.com. Go to Your account >> Account Settings >> API Keys. You will need this keys soon.

- Sign up for Mailgun free account at https://mailgun.com. You’ll need a few pieces of information from the Mailgun control panel before moving forward:

1. API Key
2. Sandbox Domain URL (should look like "sandboxc6235728hdkjehf283hajf13a90679.mailgun.org"
Both of these pieces of information can be found on the landing page of the Mailgun control panel.

- Contact Authentise to get an API key for the Design Streaming service. 

- Install Postgres: 
Mac - http://postgresapp.com/
Windows - http://www.postgresql.org/download/windows/
Ubuntu - 'apt-get install postgresql'.

- On Terminal, type psql.

```
$ psql
``` 

- If you don't have a Github account, create one. If you don't know Git, do a quick online tutorial to figure out how it works. Help: try.github.io

- Fork this repo, and then clone it locally. Help: https://help.github.com/articles/fork-a-repo/

- On Terminal, go to your forked repo.

- Also on Terminal, run the following code to install required dependencies:
```$ sudo pip install -r requirements.txt``` 

- Now export the variables for your Authentise, Mailgun and Stripe TEST keys:

```
$ export STRIPE_SECRET_KEY="your_stripe_TEST_secret_key"
```
```
$ export STRIPE_PUBLISHABLE_KEY="your_stripe_TEST_publishable_key"
```
```
$ export AUTHENTISE_API_KEY="your_authentise_key"
```
```
$ export MAILGUN_API_KEY="your_mailgun_api_key"
```
```
$ export MAILGUN_SANDBOX_DOMAIN_URL="your_mailgun_sandbox_domain_url"
```

- On `static/images` replace the file `cover.png` with the image background for your home. Ideally, it should be at least 1800 px wide.

- On `app.py`, setup your shop name and tagline:
Enter here your shop name and tagline
shop_name = "Shop name"
shop_tagline = "Best shop tagline ever"

- Run `models.py` on Terminal, to create the database:
```$ python models.py``` 

- Push  your changes to your repo:
```
$ git commit -a -m "My custom store"
$ git push
```

# Deploying it 

- First, create a Heroku account: https://signup.heroku.com/

- Install the Heroku Toolbelt: https://toolbelt.heroku.com/

- Login to Heroku on Terminal:
```
$ heroku login
Enter your Heroku credentials.
Email: your@email.com
Password:
Authentication successful.
```
- Install the Python package gunicorn
```
$ pip install gunicorn
```
- Now you are going to create a 'Procfile' with the following content 'web: gunicorn app:app --log-file=-'. If you know how to do it, good. If you don't, here's a suggestion: 
```
vim Procfile
```

You should be in the VIM editor now. Press the key 'i' in your keyboard. 

Paste or type the followin line:
```
web: gunicorn app:app --log-file=-
```

Press the key 'ESC' on your keyboard.

Type ':w' and then ':q'

To make sure it's done, display the file content doing:
```
$ cat Procfile
```
Check this works with 'foreman':

```
$ foreman start
```

- If everything is fine, add 'Procfile' to the git repo.
```
$ git add Procfile
$ git commit -m "Getting ready for Heroku"
```

- You are ready to create a new Heroku app. This creates a new app and sets up the Git remote heroku for you to push code to.
```
$ heroku create
```
- To deploy, push the code via Git:
```
$ git push heroku
```
- Wwhen the deploy is done, you should see the URL of your new Heroku app:
```
remote: -----> Discovering process types
remote:        Procfile declares types -> web
remote:
remote: -----> Compressing... done, 37.2MB
remote: -----> Launching... done, v3
remote:        https://desolate-beyond-5764.herokuapp.com/ deployed to Heroku
remote:
remote: Verifying deploy.... done.
To https://git.heroku.com/desolate-beyond-5764.git
```
You can then visit that URL in your browser.

- You can rename your app to customize your URL:
```
$ heroku rename my_store_name
```
Now your URL will be 'http://my_store_name.herokuapp.com'.

