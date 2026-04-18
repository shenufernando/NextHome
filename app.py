from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'nexthome_secret_key'

# --- MySQL Config ---


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

# --- LOGIN LOGIC (Fixed & Cleaned) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # 1. Admin Check (Hardcoded)
        if email == 'admin@gmail.com' and password == 'admin123':
            session['loggedin'] = True
            session['id'] = 0
            session['name'] = 'System Admin'
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))

        # 2. User Check (Database)
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
                return redirect(url_for('seeker_dashboard')) # Seeker dashboard එක තවම හදලා නැත්නම් index එකට යවන්න පුළුවන්
        else:
            return "<script>alert('Invalid email or password!'); window.location.href='/login';</script>"

    return render_template('login.html')

# --- ADMIN DASHBOARD ---
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'loggedin' in session and session['role'] == 'admin':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT id, name, email, role FROM users ORDER BY id DESC LIMIT 5')
        users = cursor.fetchall()
        cursor.execute('SELECT COUNT(*) as count FROM users')
        user_count = cursor.fetchone()['count']
        return render_template('admin_dashboard.html', users=users, user_count=user_count, property_count=0)
    return redirect(url_for('login'))

# --- SELLER DASHBOARD (New) ---
@app.route('/seller_dashboard')
def seller_dashboard():
    if 'loggedin' in session and session['role'] == 'seller':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Seller ගේ පෝස්ට් ලබාගැනීම
        cursor.execute('SELECT * FROM properties WHERE seller_id = %s', (session['id'],))
        my_posts = cursor.fetchall()
        
        # නොබැලූ පණිවිඩ ගණන (Notification badge එකට)
        cursor.execute('''SELECT COUNT(*) as unread FROM messages m 
                          JOIN properties p ON m.property_id = p.id 
                          WHERE p.seller_id = %s AND m.reply IS NULL''', (session['id'],))
        unread_msg = cursor.fetchone()['unread']

        return render_template('seller_dashboard.html', name=session['name'], posts=my_posts, unread=unread_msg)
    return redirect(url_for('login'))

# --- POST NEW PROPERTY (New) ---
@app.route('/add_property', methods=['GET', 'POST'])
def add_property():
    if 'loggedin' in session and session['role'] == 'seller':
        if request.method == 'POST':
            title = request.form['title']
            price = request.form['price']
            desc = request.form['description']
            package = request.form['package']
            location = request.form['location']
            
            # දින ගණන සහ මිල (Package අනුව)
            days = 30 if package == '1' else 60 if package == '2' else 90
            expiry = datetime.now() + timedelta(days=days)

            # Image Upload
            file = request.files['image']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                filename = 'default.jpg'

            # Database එකට 'pending' ලෙස දානවා
            cur = mysql.connection.cursor()
            cur.execute('''INSERT INTO properties 
                           (seller_id, title, description, price, location, image_file, package_type, expiry_date, status) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending')''', 
                        (session['id'], title, desc, price, location, filename, package, expiry))
            mysql.connection.commit()
            
            # දැනට payment පේජ් එක නැති නිසා කෙලින්ම dashboard යවමු, පස්සේ ඒක හදමු
            flash('Property added! Please complete the payment to publish.')
            return redirect(url_for('seller_dashboard'))

        return render_template('add_property.html')
    return redirect(url_for('login'))

# --- LOGOUT ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)



   

