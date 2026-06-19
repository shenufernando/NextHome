from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

# 🔑 Seeker Blueprint Create ම
seeker_bp = Blueprint('seeker_bp', __name__)

# app.py 
# app.py  initialize
mysql = None

def init_mysql(mysql_obj):
    global mysql
    mysql = mysql_obj

# --- SEEKER DASHBOARD ROUTE ---
@seeker_bp.route('/seeker_dashboard')
def seeker_dashboard():
    if 'loggedin' in session and session['role'] == 'seeker':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Approved (Live) 
        cursor.execute("SELECT * FROM properties WHERE status = 'Approved' ORDER BY id DESC")
        live_properties = cursor.fetchall()
        cursor.close()
        
        return render_template('seeker_dashboard.html', name=session['name'], properties=live_properties)
        
    return redirect(url_for('login'))

# --- SEND MESSAGE FROM SEEKER TO SELLER ---
@seeker_bp.route('/send_message/<int:property_id>', methods=['POST'])
def send_message(property_id):
    if 'loggedin' not in session or session['role'] != 'seeker':
        flash('You must be logged in as a seeker to send messages!', 'danger')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        receiver_id = request.form.get('receiver_id')
        message_text = request.form.get('message')
        sender_id = session['id']
        
        cursor = mysql.connection.cursor()
        sql = """INSERT INTO messages (property_id, sender_id, receiver_id, message) 
                 VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (property_id, sender_id, receiver_id, message_text))
        mysql.connection.commit()
        cursor.close()
        
        flash('Your message has been sent to the seller successfully!', 'success')
        return redirect(url_for('seeker_bp.seeker_dashboard')) #  Blueprint link