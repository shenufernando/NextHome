from flask import Flask, render_template, request, redirect, url_for, session, flash

from flask_mysqldb import MySQL

import MySQLdb.cursors

import os

from datetime import datetime, timedelta

from werkzeug.utils import secure_filename



app = Flask(__name__)

app.secret_key = 'nexthome_secret_key'



# --- MySQL Config ---

app.config['MYSQL_HOST'] = '127.0.0.1'

app.config['MYSQL_PORT'] = 3307

app.config['MYSQL_USER'] = 'root'

app.config['MYSQL_PASSWORD'] = '1234'

app.config['MYSQL_DB'] = 'NextHome'



# Image Upload Config

UPLOAD_FOLDER = 'static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# Upload folder එක නැත්නම් හදනවා

if not os.path.exists(UPLOAD_FOLDER):

    os.makedirs(UPLOAD_FOLDER)



mysql = MySQL(app)



# --- ROUTES ---



@app.route('/')

def home():

    return render_template('index.html')



# --- SIGNUP LOGIC ---

@app.route('/signup', methods=['GET', 'POST'])

def signup():

    if request.method == 'POST':

        name = request.form['name']

        email = request.form['email']

        password = request.form['password']

        role = request.form['role']



        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)", (name, email, password, role))

        mysql.connection.commit()

        cur.close()

       

        return redirect(url_for('login'))

    return render_template('signup.html')





# --- LOGIN LOGIC ---

@app.route('/login', methods=['GET', 'POST'])

def login():

    if request.method == 'POST':

        email = request.form['email']

        password = request.form['password']



        # ⭐ ADMIN CHECK (Blueprint එකට redirect වේ)

        if email == 'admin@gmail.com' and password == 'admin123':

            session['loggedin'] = True

            session['id'] = 0

            session['name'] = 'System Admin'

            session['role'] = 'admin'

            return redirect(url_for('admin_bp.admin_dashboard'))



        # User Check (Database)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))

        account = cursor.fetchone()



        if account:

            session['loggedin'] = True

            session['id'] = account['id']

            session['name'] = account['name']

            session['role'] = account['role']

           

            if account['role'] == 'seller':

                return redirect(url_for('seller_dashboard'))

            else:

                return redirect(url_for('home'))

        else:

            return "<script>alert('Invalid email or password!'); window.location.href='/login';</script>"



    return render_template('login.html')





# --- SELLER DASHBOARD ---

@app.route('/seller_dashboard')

def seller_dashboard():

    if 'loggedin' in session and session['role'] == 'seller':

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

       

        # Seller ගේ පෝස්ට් ලබාගැනීම

        cursor.execute('SELECT * FROM properties WHERE seller_id = %s', (session['id'],))

        my_posts = cursor.fetchall()

       

        # නොබැලූ පණිවිඩ ගණන

        cursor.execute('''SELECT COUNT(*) as unread FROM messages m

                          JOIN properties p ON m.property_id = p.id

                          WHERE p.seller_id = %s AND m.reply IS NULL''', (session['id'],))

        unread_msg = cursor.fetchone()['unread']

        cursor.close()



        return render_template('seller_dashboard.html', name=session['name'], posts=my_posts, unread=unread_msg)

    return redirect(url_for('login'))





# --- POST NEW PROPERTY (Payment එකට සම්බන්ධ කර ඇත) ---

@app.route('/add_property', methods=['GET', 'POST'])

def add_property():

    if 'id' not in session:

        return redirect(url_for('login'))



    if request.method == 'POST':

        # Form එකේ දත්ත ටික තාවකාලිකව session එකට දාමු

        session['temp_post'] = {

            'title': request.form.get('title'),

            'category': request.form.get('category'),

            'location': request.form.get('location'),

            'price': request.form.get('price'),

            'description': request.form.get('description'),

            'package': request.form.get('package', '1')

        }



        # පින්තූරය සේව් කර නම session එකට දාමු

        file = request.files.get('image')

        if file and file.filename != '':

            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            session['temp_post']['image_file'] = filename

        else:

            session['temp_post']['image_file'] = 'default.jpg'



        return redirect(url_for('payment'))



    return render_template('add_property.html')





# --- PAYMENT LOGIC ---

@app.route('/payment', methods=['GET', 'POST'])

def payment():

    if 'temp_post' not in session:

        return redirect(url_for('add_property'))



    if request.method == 'POST':

        post_data = session['temp_post']

        days = 30 if post_data['package'] == '1' else 60 if post_data['package'] == '2' else 90

        expiry_date = datetime.now() + timedelta(days=days)



        # Database එකට 'Approved' විදිහටම ඇතුළත් කරනවා

        cursor = mysql.connection.cursor()

        sql = """INSERT INTO properties

                 (title, description, category, location, price, expiry_date, image_file, seller_id, status)

                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Approved')"""

       

        cursor.execute(sql, (

            post_data['title'], post_data['description'], post_data['category'],

            post_data['location'], post_data['price'], expiry_date,

            post_data['image_file'], session['id']

        ))

       

        mysql.connection.commit()

        cursor.close()



        # වැඩේ ඉවර නිසා තාවකාලික දත්ත අයින් කරනවා

        session.pop('temp_post', None)

       

        flash('Payment Successful! Your property is now published.')

        return redirect(url_for('seller_dashboard'))



    return render_template('payment.html', post=session['temp_post'])





# --- LOGOUT ---

@app.route('/logout')

def logout():

    session.clear()

    return redirect(url_for('login'))





# --- BLUEPRINT REGISTRATION (සියලුම රවුට් වලට පසුව අවසානයටම) ---

from admin import admin_bp

app.register_blueprint(admin_bp)



if __name__ == '__main__':

    app.run(debug=True, port=5000)


 