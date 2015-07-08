# Authentise-Store


Directions

- Signup for Stripe.com. Go to Your account >> Account Settings >> API Keys. You will need this keys soon.

- Contact Authentise to get an API key for the Design Streaming service. 

- If you don't have a Github account, create one. If you don't know Git, do a quick online tutorial to figure out how it works: try.github.io

- Fork this repo, and then clone it locally so that you have these files: https://help.github.com/articles/fork-a-repo/

- Before you start, run the following code in your Terminal to install required dependencies:
```sudo pip install -r requirements.txt``` 

- On `app.py`, setup your shop name and tagline:
# Enter here your shop name and tagline
shop_name = "Shop name"
shop_tagline = "Best shop tagline ever"

- On `models.py`, setup you Stripe and Authentise keys:
# SETUP: Enter here your STRIPE keys
stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']
<code>
# SETUP: Enter here your AUTHENTISE key
AUTHENTISE_KEY = os.environ['AUTHENTISE_API_KEY']
</code>

- On `static/images` replace the file `cover.png` with the image background for your home. Ideally, it should be at least 1800 px wide.
- 



