from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

#  Seeker Blueprint Create 
seeker_bp = Blueprint('seeker_bp', __name__)


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
        return redirect(url_for('seeker_bp.seeker_dashboard'))



@seeker_bp.route('/my_messages')
def my_messages():
    if 'loggedin' not in session or session['role'] != 'seeker':
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Seeker 
    cursor.execute("""
        SELECT m.*, p.title AS property_title, u.name AS seller_name
        FROM messages m
        JOIN properties p ON m.property_id = p.id
        JOIN users u ON p.seller_id = u.id
        WHERE m.sender_id = %s
        ORDER BY m.id DESC
    """, (session['id'],))
    
    messages = cursor.fetchall()
    cursor.close()
    return render_template('seeker_messages.html', messages=messages)


@seeker_bp.route('/send_followup/<int:property_id>/<int:receiver_id>', methods=['POST'])
def send_followup(property_id, receiver_id):
    if 'loggedin' not in session or session['role'] != 'seeker':
        return redirect(url_for('login'))
        
    followup_text = request.form.get('followup_text')
    
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO messages (property_id, sender_id, receiver_id, message)
        VALUES (%s, %s, %s, %s)
    """, (property_id, session['id'], receiver_id, followup_text))
    
    mysql.connection.commit()
    cursor.close()
    flash('Follow-up message sent successfully!', 'success')
    return redirect(url_for('seeker_bp.my_messages'))