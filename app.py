from bson import ObjectId
from flask import Flask, session
from pymongo import MongoClient
from flask_login import LoginManager
from flask import Flask, render_template, request, redirect, url_for
from flask import session
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from propelauth_flask import init_auth, current_user, current_org
from tensorflow import keras
import numpy as np
import random

app = Flask(__name__)
client = MongoClient('mongodb://localhost:3017/')
db = client['BoozeBuddy']
genders = ['Male', 'Female']

@app.route('/')
def default():
    user = session.get('user')
    if user is None:
        # Handle the case where there is no user in the session.
        # For example, redirect to the login page or return a message.
        return redirect(url_for('details'))

    name = user.get('name')
    weight = user.get('weight')
    height = user.get('height')
    gender = user.get('gender')

    widmark = 0.55 
    if gender == 'Male': 
        widmark = 0.68 

    bac = round(14 / (weight * 453.6 * widmark) * 100, 2)
    downtime = round((bac/0.015), 2)

    return render_template('home-page-booze-buddy.html', downtime=downtime, name=name, gender=gender, weight=weight, height=height, user=user, widmark=widmark, bac=bac)
    user = session.get('user')
    name = user.get('name')
    weight = user.get('weight')
    height = user.get('height')
    gender = user.get('gender')

    widmark = 0.55 
    if gender == 'Male': 
        widmark = 0.68 

    bac = round(14 / (user.get('weight') * 453.6 * widmark) * 100, 2)
    downtime = round((bac/0.015), 2)

    return render_template('home-page-booze-buddy.html', downtime = downtime, name = name, gender = gender, weight = weight, height = height, user = user, widmark = widmark, bac = bac)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users = db.users

        name = request.form['name']
        email = request.form['email']

        # Check if email already exists in the database
        existing_user = users.find_one({'email': email})
        if existing_user:
            return "user already exists with this email"

        password = request.form['password']
        age = request.form['age']
        gender = request.form['gender']
        height = float(request.form['height'])
        weight = float(request.form['weight'])

        new_user = {
            'name': name, 
            'email': email,
            'password': password,
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight
        }
        users.insert_one(new_user)

        return redirect(url_for('login'))

    return render_template('index.html', genders = genders)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = db.users

        email = request.form['email']
        password = request.form['password']

        existing_user = users.find_one({'email': email, 'password': password})

        if existing_user:
            existing_user['_id'] = str(existing_user['_id'])
            session['user'] = existing_user

            return redirect('/')  # Redirect if user doesn't exist

    return render_template('login.html')  # Redirect only if user exists and password matches

@app.route('/dashboard')
def dashboard():
    user = session.get('user')
    widmark = 0.55 

    if user.get('gender') == 'Male': 
        widmark = 0.68 

    bac = round(14 / (user.get('weight') * 453.6 * widmark) * 100, 2)

    downtime = (bac/0.015)

    return render_template('dashboard.html', user = user, widmark = widmark, bac = bac, downtime = downtime)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        field = request.form.get('field')
        query = request.form.get('query')
        if field:
            if field == 'name':
                results = db.drinks.find({'name': {'$regex': query, '$options': 'i'}})
            elif field == 'type':
                results = db.drinks.find({'type': {'$regex': query, '$options': 'i'}})
            elif field == 'abv':
                results = db.drinks.find({'abv': {'$regex': query, '$options': 'i'}})
            elif field == 'mixes':
                results = db.drinks.find({'mixes': {'$regex': query, '$options': 'i'}})
            else:
                results = None
        else:
            # If no field is specified, return all entries
            results = db.drinks.find()
            query = "all drinks"
        return render_template('search-results.html', results=results, query=query)
    return render_template('search-results.html')

@app.route('/resources')
def resources():
    return render_template('resources-boozebuddy.html')

@app.route('/details')
def details():
    drink_id = request.args.get('drink_id')

    drink = db.drinks.find_one({'_id': ObjectId(drink_id)})

    limit = round(0.6 / (drink.get('abv') / 100), 2)

    return render_template('details.html', drink = drink, limit = limit)

@app.route('/terms')
def terms():
    results = db.terms.find()
    return render_template('terms.html', results = results)

@app.route('/profile')
def profile():
    user = session.get('user')
    return render_template('profile.html', user = user)

@app.route('/like')
def like():
    user = session.get('user')
    user_id = user.get('_id')
    drink_id = request.args.get('drink_id')
    drink = db.drinks.find_one({'_id': ObjectId(drink_id)})

    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"liked": drink_id}}
    )

    return render_template('search-results.html')

@app.route('/logout')
def logout():
    session.clear()

    return redirect(url_for('signup'))

@app.route('/recommendations')
def recommendations():
    if (db.users.liked.length > 0):
        model = keras.load_models('model.h5')
        random_numbers = [random.randint(0, 99) for _ in range(20)]
        input_data = np.array(random_numbers).reshape(1, -1)
        prediction = model.predict(input_data)
        print("Prediction:", prediction)
        return render_template('recommendations.html', prediction = prediction)
    return render_template('recommendations.html')



def predict_with_random_numbers(model):
    random_numbers = [random.randint(0, 99) for _ in range(20)]

    input_data = np.array(random_numbers).reshape(1, -1)
    
    prediction = model.predict(input_data)
    
    print("Random Numbers:", random_numbers)
    print("Prediction:", prediction)
    
    return prediction

model = keras.load_models('model.h5')

predict_with_random_numbers(model)

# @app.route('/update', methods=['POST'])
# def update_user():
#     # Retrieve form data
#     age = request.form.get('age')
#     gender = request.form.get('gender')
#     height = request.form.get('height')
#     weight = request.form.get('weight')
    


#     return redirect(url_for('profile'))  

if __name__ == '__main__':
    app.secret_key = 'hoohacks'
    app.run(debug=True)

