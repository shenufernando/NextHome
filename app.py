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
            
            # 🔄role
            if account['role'] == 'seller':
                return redirect(url_for('seller_dashboard'))
            elif account['role'] == 'seeker':
                # මෙ Seeker Blueprint link:
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

@app.route('/contact')
def contact():
    return render_template('contact.html')

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

# --- POST NEW PROPERTY (Fixed with Multi-Image Upload & Expiry Logistics) ---
@app.route('/add_property', methods=['GET', 'POST'])
def add_property():
    if 'id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        contact_phone = request.form.get('contact_phone')
        
        raw_type = request.form.get('type', '')
        if 'land' in raw_type.lower():
            property_type = 'Land'
        else:
            property_type = 'House'

        location = request.form.get('location')
        selected_plan = request.form.get('plan', 'basic')

        # 📅 EXPIRED & STATUS LOGISTICS
        if selected_plan == 'premium':
            status = 'Pending_Approval'
            # Premium  30 days Expire වීම 
            expiry_date = datetime.now() + timedelta(days=30)
        else:
            status = 'pending'
            expiry_date = datetime.now() + timedelta(days=14)

        # 📸 IMAGE UPLOAD LOGIC (image 6)
        saved_images = []
        for i in range(1, 7):
            file = request.files.get(f'image{i}')
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                #  Timestamp 
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                saved_images.append(unique_filename)

        #  default image
        if not saved_images:
            image_url_value = 'default.jpg'
        else:
            image_url_value = ",".join(saved_images) # ex: "img1.jpg,img2.jpg,img3.jpg"

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
            flash('Premium Listing submitted! It will be open for payment once Admin approves it.', 'success')
        else:
            flash('Property posted successfully! Pending admin approval.', 'success')

        return redirect(url_for('seller_dashboard'))

    return render_template('add_property.html')

# --- PREMIUM CONFIRM, UPDATE PROPERTY & SAVE PAYMENT (ALL IN ONE) ---
@app.route('/pay_premium/<int:post_id>', methods=['POST'])
def pay_premium(post_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))
        
    seller_id = session['id']
    cursor = mysql.connection.cursor()
    
    try:
        # 1. properties, status  ,Approved , premium 
        exact_expiry = datetime.now() + timedelta(days=30)
        cursor.execute("""
            UPDATE properties 
            SET status = 'Approved', plan = 'premium', expiry_date = %s 
            WHERE id = %s AND seller_id = %s
        """, (exact_expiry, post_id, seller_id))
        
        # 2. payments Rs. 3000 
        cursor.execute("""
            INSERT INTO payments (property_id, seller_id, amount, payment_status) 
            VALUES (%s, %s, %s, %s)
        """, (post_id, seller_id, 3000.00, 'completed'))
        
       
        mysql.connection.commit()
        flash('Payment Successful! Your Premium post is now Live for 30 Days.', 'success')
        
    except Exception as e:
        mysql.connection.rollback() 
        print(f"Payment Error: {e}")
        flash('Something went wrong with the payment. Please try again.', 'danger')
        
    finally:
        cursor.close()
        
    return redirect(url_for('seller_dashboard'))


# --- EDIT PROPERTY ---
@app.route('/edit_property/<int:property_id>', methods=['GET', 'POST'])
def edit_property(property_id):
    if 'id' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'GET':
        cursor.execute("SELECT * FROM properties WHERE id = %s AND seller_id = %s", (property_id, session['id']))
        property_data = cursor.fetchone()
        cursor.close()
        if property_data:
            return render_template('edit_property.html', property=property_data)
        return redirect(url_for('seller_dashboard'))

    elif request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        contact_phone = request.form.get('contact_phone')
        location = request.form.get('location')

        cursor.execute("""
            UPDATE properties 
            SET title=%s, description=%s, price=%s, contact_phone=%s, location=%s 
            WHERE id=%s AND seller_id=%s
        """, (title, description, price, contact_phone, location, property_id, session['id']))
        
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('seller_dashboard'))

# --- DELETE PROPERTY ---
@app.route('/delete_property/<int:property_id>')
def delete_property(property_id):
    if 'id' not in session:
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor()
    
    cursor.execute("DELETE FROM properties WHERE id = %s AND seller_id = %s", (property_id, session['id']))
    mysql.connection.commit()
    cursor.close()
    
    return redirect(url_for('seller_dashboard'))

# --- PROFILE SETTINGS DUMMY ROUTE (To fix BuildError) ---
@app.route('/profile_settings')
def profile_settings():
    return "Profile Settings Page (Under Construction)"


# --- SELLER MESSAGES VIEW (UPDATED FOR BUYER NAME & EMAIL) ---
@app.route('/messages')
def messages():
    if 'loggedin' in session and session['role'] == 'seller':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
       
        cursor.execute('''SELECT m.*, u.name AS sender_name, u.email AS sender_email, p.title as property_title 
                          FROM messages m
                          LEFT JOIN users u ON m.sender_id = u.id
                          JOIN properties p ON m.property_id = p.id
                          WHERE p.seller_id = %s 
                          ORDER BY m.id DESC''', (session['id'],))
        all_messages = cursor.fetchall()
        
        cursor.execute('''SELECT COUNT(*) as unread FROM messages m
                          JOIN properties p ON m.property_id = p.id
                          WHERE p.seller_id = %s AND m.reply IS NULL''', (session['id'],))
        unread_msg = cursor.fetchone()['unread']
        cursor.close()

        return render_template('messages.html', name=session['name'], messages=all_messages, unread=unread_msg)
    return redirect(url_for('login'))

# --- REPLY TO SEEKER MESSAGE ROUTE (UPDATED FOR REDIRECT FIX) ---
@app.route('/reply_message/<int:message_id>', methods=['POST'])
def reply_message(message_id):
    if 'loggedin' in session and session['role'] == 'seller':
        reply_text = request.form.get('reply_text')
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE messages SET reply = %s WHERE id = %s", (reply_text, message_id))
        mysql.connection.commit()
        cursor.close()
        flash('Reply sent successfully!', 'success')
        return redirect(url_for('messages'))
    return redirect(url_for('login'))

# --- LOGOUT ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- BLUEPRINT REGISTRATION ---

# 1. Admin Blueprint
from admin import admin_bp
app.register_blueprint(admin_bp)

# 2. Seeker Blueprint 
from seeker import seeker_bp, init_mysql
init_mysql(mysql)  
app.register_blueprint(seeker_bp)


if __name__ == '__main__':
    app.run(debug=True, port=5000)