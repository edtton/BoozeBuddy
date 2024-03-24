from flask import Flask
from pymongo import MongoClient
from propelauth_flask import init_auth
from flask_login import LoginManager
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from flask import session

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['BoozeBuddy']
genders = ['Male', 'Female']

@app.route('/')
def default():
    user = session.get('user')
    name = user.get('name')
    weight = user.get('weight')
    height = user.get('height')
    gender = user.get('gender')

    widmark = 0.55 
    if gender == 'Male': 
        widmark = 0.68 

    bac = round(14 / (user.get('weight') * 453.6 * widmark) * 100, 2)

    return render_template('home-page-booze-buddy.html', name = name, gender = gender, weight = weight, height = height, user = user, widmark = widmark, bac = bac)

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

    return render_template('dashboard.html', user = user, widmark = widmark, bac = bac)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        field = request.form.get('field')
        query = request.form.get('query')
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
        return render_template('search.html', results = results)
    return render_template('search.html')

@app.route('/resources')
def resources():
    return render_template('resources-boozebuddy.html')
    

if __name__ == '__main__':
    app.secret_key = 'hoohacks'
    app.run(debug=True)

