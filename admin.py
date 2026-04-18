from flask import Blueprint, render_template, session, redirect, url_for
import MySQLdb.cursors

# Admin සඳහා Blueprint එකක් සෑදීම
admin_bp = Blueprint('admin', __name__)

# මෙතන 'mysql' object එක ලබාගන්න ක්‍රමයක් අවශ්‍යයි
# ඒ නිසා අපි function එකක් ඇතුළේ mysql එක පාවිච්චි කරමු
def init_admin(mysql_instance):
    global mysql
    mysql = mysql_instance

@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'loggedin' in session and session['role'] == 'admin':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # 1. Users ලා 5 දෙනා ලබාගැනීම
        cursor.execute('SELECT id, name, email, role FROM users ORDER BY id DESC LIMIT 5')
        users = cursor.fetchall()

        # 2. මුළු Users ගණන
        cursor.execute('SELECT COUNT(*) as count FROM users')
        user_count = cursor.fetchone()['count']

        property_count = 0 

        return render_template('admin_dashboard.html', users=users, user_count=user_count, property_count=property_count)
    
    return redirect(url_for('login'))

@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))