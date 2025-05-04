from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import hashlib  # For hashing passwords
from model import recommend, get_persona   # Ensure this exists in model.py

app = Flask(__name__)
app.secret_key = 'a2f317f60abd436044914aebac4c2a7f'  # Required for sessions

# Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'test'
app.config['MYSQL_PASSWORD'] = 'test'
app.config['MYSQL_DB'] = 'persona'

mysql = MySQL(app)


@app.route('/')
def index():
    return redirect(url_for('welcome'))  # Redirect to registration page

@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    return render_template('welcome.html')


# ---------- Registration ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        Full_name = request.form['Full_name']
        email = request.form['email']
        DoB = request.form['DoB']
        password = request.form['password']

        if not Full_name or not email or not DoB or not password:
            flash("All fields are required.")
            return redirect(url_for('register'))

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM profile WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash("Email already registered. Please login or use another email.")
            cursor.close()
            return redirect(url_for('register'))

        cursor.execute(
            "INSERT INTO profile (Full_name, email, DoB, password) VALUES (%s, %s, %s, %s)",
            (Full_name, email, DoB, password_hash)
        )
        mysql.connection.commit()

        cursor.execute("SELECT user_id FROM profile WHERE email = %s", (email,))
        user = cursor.fetchone()
        session['user_id'] = user[0]
        cursor.close()

        return redirect(url_for('persona'))
    return render_template('reg.html')

# ---------- Login ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Both email and password are required.")
            return redirect(url_for('login'))

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM profile WHERE email = %s AND password = %s", (email, hashed_password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['user_id'] = user[0]
            persona, keywords = user[4], user[5]

            if persona and keywords:
                return redirect(url_for('home'))
            else:
                return redirect(url_for('persona'))
        else:
            flash("Invalid credentials. Please try again.")
            return redirect(url_for('login'))

# ---------- Persona Form ----------
@app.route('/persona', methods=['GET', 'POST'])
def persona():
    if 'user_id' not in session:
        flash("Please login to access this page.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        persona = request.form['persona']
        keywords = request.form['keywords']
        age_group = request.form['age_group']
        travel_style = request.form['travel_style']
        budget = request.form['budget']

        if not persona or not keywords:
            flash("Persona and keywords are required.")
            return redirect(url_for('persona'))

        session['persona'] = persona
        session['keywords'] = keywords
        session['age_group'] = age_group
        session['travel_style'] = travel_style
        session['budget'] = budget

        cursor = mysql.connection.cursor()
        cursor.execute(
            """UPDATE profile 
            SET persona = %s, keywords = %s, 
                age_group = %s, travel_style = %s, budget = %s 
            WHERE user_id = %s""",
            (persona, keywords, age_group, travel_style, budget, session['user_id'])
        )
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('home'))

    return render_template('persona.html')


# ---------- Logout ----------
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.")
    return redirect(url_for('login'))


@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'user_id' not in session:
        flash("Login required to view this page.")
        return redirect(url_for('login'))

    preferred_subtype = session.get('persona')
    keywords = session.get('keywords')
    age_group = session.get('age_group')
    travel_style = session.get('travel_style')
    budget = session.get('budget')

    if not preferred_subtype:
        flash("Persona selection is missing.")
        return redirect(url_for('persona'))

    if keywords:
        if isinstance(keywords, str):
            keywords = keywords.lower().split(',')
            keywords = [kw.strip() for kw in keywords if kw.strip()]

    recommendations = recommend(
        preferred_subtype=preferred_subtype,
        keywords=keywords,
        age_group=age_group,
        travel_style=travel_style,
        budget=budget
    )

    return render_template('recommendation.html', recommendations=recommendations)

@app.route('/profile', methods=['GET'])
def profile():
    if 'user_id' not in session:
        flash("Login required to view profile.")
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM profile WHERE user_id = %s", (session['user_id'],))
    user_data = cursor.fetchone()
    cursor.close()

    if user_data:
        return render_template('view_profile.html', user_data=user_data)
    else:
        flash("Profile not found.")
        return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash("Login required to edit profile.")
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM profile WHERE user_id = %s", (session['user_id'],))
    user_data = cursor.fetchone()

    if not user_data:
        flash("Unable to fetch profile.")
        cursor.close()
        return redirect(url_for('profile'))

    if request.method == 'POST':
        full_name = request.form['Full_name']
        email = request.form['email']
        dob = request.form['DoB']
        persona = request.form.get('persona')
        keywords = request.form.get('keywords')
        age_group = request.form.get('age_group')
        travel_style = request.form.get('travel_style')
        budget = request.form.get('budget')

        updates = []
        values = []

        if full_name:
            updates.append("Full_name = %s")
            values.append(full_name)
        if email:
            updates.append("email = %s")
            values.append(email)
        if dob:
            updates.append("DoB = %s")
            values.append(dob)
        if persona:
            updates.append("persona = %s")
            values.append(persona)
        if keywords:
            updates.append("keywords = %s")
            values.append(keywords)
        if age_group:
            updates.append("age_group = %s")
            values.append(age_group)
        if travel_style:
            updates.append("travel_style = %s")
            values.append(travel_style)
        if budget:
            updates.append("budget = %s")
            values.append(budget)

        if updates:
            values.append(session['user_id'])
            query = f"UPDATE profile SET {', '.join(updates)} WHERE user_id = %s"
            cursor.execute(query, tuple(values))
            mysql.connection.commit()
            flash("Profile updated successfully.")

        cursor.close()
        return redirect(url_for('profile'))

    cursor.close()
    return render_template('edit_profile.html', user_data=user_data)

@app.route("/destinations")
def destinations():
    return render_template("destinations.html")

@app.route('/info2.html')
def info2():
    place_id = request.args.get('id')
    if place_id:
        return render_template('info2.html', place_id=place_id)
    else:
        return "Destination not found, this is printed from app.py", 404

if __name__ == '__main__':
    app.run(debug=True)
