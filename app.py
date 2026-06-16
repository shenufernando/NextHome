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

        if email == 'admin@gmail.com' and password == 'admin123':
            session['loggedin'] = True
            session['id'] = 0
            session['name'] = 'System Admin'
            session['role'] = 'admin'
            return redirect(url_for('admin_bp.admin_dashboard'))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['name'] = account['name']
            session['role'] = account['role']
            
            # 🔄 රෝල් එක අනුව අදාළ ඩෑෂ්බෝඩ් එකට යැවීම
            if account['role'] == 'seller':
                return redirect(url_for('seller_dashboard'))
            elif account['role'] == 'seeker':
                # 🎯 මෙතනට Seeker Blueprint එකේ ලින්ක් එක එකතු කළා:
                return redirect(url_for('seeker_bp.seeker_dashboard'))
            else:
                return redirect(url_for('home'))
        else:
            return "<script>alert('Invalid email or password!'); window.location.href='/login';</script>"

    return render_template('login.html')


@app.route('/about')
def about():
    return render_template('about_us.html')

@app.route('/manual')
def manual():
    return render_template('user_manual.html')

# --- SELLER DASHBOARD ---
@app.route('/seller_dashboard')
def seller_dashboard():
    if 'loggedin' in session and session['role'] == 'seller':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute('SELECT * FROM properties WHERE seller_id = %s', (session['id'],))
        my_posts = cursor.fetchall()
        
        cursor.execute('''SELECT COUNT(*) as unread FROM messages m
                          JOIN properties p ON m.property_id = p.id
                          WHERE p.seller_id = %s AND m.reply IS NULL''', (session['id'],))
        unread_msg = cursor.fetchone()['unread']
        cursor.close()

        return render_template('seller_dashboard.html', name=session['name'], posts=my_posts, unread=unread_msg)
    return redirect(url_for('login'))

# --- POST NEW PROPERTY (Fixed with exact column synchronization) ---
# --- POST NEW PROPERTY (Fixed For Enum Column Error) ---
# --- POST NEW PROPERTY (Fixed For Strict MySQL ENUM Column) ---
@app.route('/add_property', methods=['GET', 'POST'])
def add_property():
    if 'id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        contact_phone = request.form.get('contact_phone')
        
        # HTML Dropdown එකෙන් එන Value එක ලබා ගැනීම
        raw_type = request.form.get('type', '')
        
        # 🚨 ENUM Error එක 100% නැති කරන Logic එක:
        # ඔයාගේ HTML එකෙන් මොන වචනය ආවත්, ඩේටාබේස් ENUM එකට ගැලපෙන නිවැරදිම වචනය මෙතනින් තෝරනවා.
        # (ඔයාගේ DB එකේ තියෙන වචන 'House' සහ 'Land' නම් මේක හරියටම මැච් වෙනවා)
        if 'land' in raw_type.lower():
            property_type = 'Land'
        else:
            property_type = 'House' # Default එක විදිහට House දානවා

        location = request.form.get('location')
        selected_plan = request.form.get('plan', 'basic')

        if selected_plan == 'premium':
            status = 'Pending_Approval'
            expiry_date = datetime.now() + timedelta(days=60)
        else:
            status = 'pending'
            expiry_date = datetime.now() + timedelta(days=14)

        file = request.files.get('image1')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url_value = filename
        else:
            image_url_value = 'default.jpg'

        cursor = mysql.connection.cursor()
        sql = """INSERT INTO properties 
                 (seller_id, title, description, price, location, contact_phone, type, plan, status, expiry_date, image_url, package) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        cursor.execute(sql, (
            session['id'], title, description, price, location, contact_phone,
            property_type, selected_plan, status, expiry_date, image_url_value, selected_plan
        ))
        
        mysql.connection.commit()
        cursor.close()

        if selected_plan == 'premium':
            flash('Premium Listing submitted! It will be open for payment once Admin approves it.')
        else:
            flash('Property posted successfully! Pending admin approval.')

        return redirect(url_for('seller_dashboard'))

    return render_template('add_property.html')

# --- PREMIUM CONFIRM & PUBLISH ROUTE ---
@app.route('/pay_premium/<int:post_id>', methods=['POST'])
def pay_premium(post_id):
    if 'id' not in session:
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE properties SET status = 'Approved' WHERE id = %s AND seller_id = %s", (post_id, session['id']))
    mysql.connection.commit()
    cursor.close()
    
    flash('Payment Successful! Your Premium post is now Live.')
    return redirect(url_for('seller_dashboard'))

# --- PROFILE SETTINGS DUMMY ROUTE (To fix BuildError) ---
@app.route('/profile_settings')
def profile_settings():
    return "Profile Settings Page (Under Construction)"

# --- LOGOUT ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- BLUEPRINT REGISTRATION ---

# 1. Admin Blueprint එක (දැනටමත් තිබුණ එක)
from admin import admin_bp
app.register_blueprint(admin_bp)

# 2. Seeker Blueprint එක (අලුතින් එකතු කළ යුත්තේ මේ විදිහටයි)
from seeker import seeker_bp, init_mysql
init_mysql(mysql)  # app.py එකේ තියෙන mysql object එක seeker එකට පාස් කරනවා
app.register_blueprint(seeker_bp)

# 🚨 සේරටම පස්සේ තමයි ඇප් එක රන් වෙන්න ඕනේ!
if __name__ == '__main__':
    app.run(debug=True, port=5000)