# Authentise-Store


First, get it ready to run locally:

- Signup for Stripe.com. Go to Your account >> Account Settings >> API Keys. You will need this keys soon.

- Contact Authentise to get an API key for the Design Streaming service. 

- If you don't have a Github account, create one. If you don't know Git, do a quick online tutorial to figure out how it works. Help: try.github.io

- Fork this repo, and then clone it locally. Help: https://help.github.com/articles/fork-a-repo/

- On Terminal, go to your forkeg repo.

- Also on Terminal, run the following code to install required dependencies:
```$ sudo pip install -r requirements.txt``` 

- Now export the variables for your Authentise and Stripe TEST keys:
```
$ export SECRET_KEY=your_stripe_test_secret_key
```
```
$ export PUBLISHABLE_KEY=your_stripe_test_publishable_key
```
```
$ export AUTHENTISE_API_KEY=your_authentise_key
```

- On `static/images` replace the file `cover.png` with the image background for your home. Ideally, it should be at least 1800 px wide.

- On `app.py`, setup your shop name and tagline:
Enter here your shop name and tagline
shop_name = "Shop name"
shop_tagline = "Best shop tagline ever"

- Run `models.py` on Terminal, to create the database:
```$ python models.py``` 


