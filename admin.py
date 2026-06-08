from flask import Blueprint, render_template, session, redirect, url_for, request, flash
import MySQLdb.cursors

admin_bp = Blueprint('admin_bp', __name__)

# --- 1. ADMIN DASHBOARD ---
@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'loggedin' in session and session['role'] == 'admin':
        from app import mysql
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # අලුත්ම යූසර්ස්ලා 5 දෙනා ලබාගැනීම
        cursor.execute('SELECT id, name, email, role FROM users ORDER BY id DESC LIMIT 5')
        users = cursor.fetchall()

        # මුළු යූසර්ස්ලා ගණන
        cursor.execute('SELECT COUNT(*) as count FROM users')
        user_count = cursor.fetchone()['count']
        
        # මුළු Properties ගණන
        cursor.execute('SELECT COUNT(*) as count FROM properties')
        property_count = cursor.fetchone()['count']
        
        # Approve කිරීමට බලාපොරොත්තුවෙන් පවතින (Pending) Properties ලැයිස්තුව
        cursor.execute("SELECT * FROM properties WHERE status = 'pending' ORDER BY id DESC")
        pending_properties = cursor.fetchall()
        
        cursor.close()

        return render_template('admin_dashboard.html', 
                               users=users, 
                               user_count=user_count, 
                               property_count=property_count,
                               pending_properties=pending_properties)
    
    return redirect(url_for('login'))


# --- ⭐ APPROVE PROPERTY ROUTE ---
@admin_bp.route('/approve_property/<int:id>')
def approve_property(id):
    if 'loggedin' in session and session['role'] == 'admin':
        from app import mysql
        cursor = mysql.connection.cursor()
        # Status එක 'Approved' ලෙස යාවත්කාලීන කිරීම
        cursor.execute("UPDATE properties SET status = 'Approved' WHERE id = %s", (id,))
        mysql.connection.connection.commit()
        cursor.close()
        flash("Property approved and published successfully!", "success")
        return redirect(url_for('admin_bp.admin_dashboard'))
    return redirect(url_for('login'))


# --- ⭐ REJECT / DELETE PROPERTY ROUTE ---
@admin_bp.route('/reject_property/<int:id>')
def reject_property(id):
    if 'loggedin' in session and session['role'] == 'admin':
        from app import mysql
        cursor = mysql.connection.cursor()
        # සදහටම ඩේටාබේස් එකෙන් ඉවත් කිරීම හෝ status එක 'Rejected' කිරීම (මෙහිදී delete කර ඇත)
        cursor.execute("DELETE FROM properties WHERE id = %s", (id,))
        mysql.connection.connection.commit()
        cursor.close()
        flash("Property listing rejected and removed.", "danger")
        return redirect(url_for('admin_bp.admin_dashboard'))
    return redirect(url_for('login'))


# --- 2. MANAGE USERS ---
@admin_bp.route('/manage_users')
def manage_users():
    if 'loggedin' in session and session['role'] == 'admin':
        from app import mysql
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute("SELECT id, name, email, role, status FROM users")
        users = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as total FROM users")
        total_users = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role='seeker'")
        total_seekers = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role='seller'")
        total_sellers = cursor.fetchone()['total']
        
        cursor.close()
        
        return render_template('manage_users.html', 
                               users=users, 
                               total_users=total_users, 
                               total_seekers=total_seekers, 
                               total_sellers=total_sellers)
        
    return redirect(url_for('login'))


# --- 3. EDIT USER (POP-UP MODAL UPDATE) ---
@admin_bp.route('/edit_user/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    if 'loggedin' in session and session['role'] == 'admin':
        from app import mysql
        cursor = mysql.connection.cursor()
        
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        
        cursor.execute('UPDATE users SET name=%s, email=%s, role=%s WHERE id=%s', (name, email, role, user_id))
        mysql.connection.commit()
        cursor.close()
        
        return redirect(url_for('admin_bp.manage_users'))
        
    return redirect(url_for('login'))


# --- 4. BLOCK / ACTIVE STATUS TOGGLE ---
@admin_bp.route('/toggle_user_status/<int:user_id>')
def toggle_user_status(user_id):
    if 'loggedin' in session and session['role'] == 'admin':
        from app import mysql
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute("SELECT status FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        
        if user:
            new_status = 'blocked' if user['status'] == 'active' else 'active'
            cursor.execute("UPDATE users SET status=%s WHERE id=%s", (new_status, user_id))
            mysql.connection.commit()
            
        cursor.close()
        return redirect(url_for('admin_bp.manage_users'))
        
    return redirect(url_for('login'))


# --- 5. DELETE USER permanently ---
@admin_bp.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'loggedin' in session and session['role'] == 'admin':
        from app import mysql
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('admin_bp.manage_users'))
        
    return redirect(url_for('login'))


# --- 6. LOGOUT ---
@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# --- 7. ADMIN SETTINGS PAGE ---
@admin_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'loggedin' in session and session['role'] == 'admin':
        from app import mysql
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute("SELECT id, name, email FROM users WHERE id=%s", (session['id'],))
        admin_info = cursor.fetchone()
        
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            new_password = request.form['password']
            
            if new_password:
                cursor.execute("UPDATE users SET name=%s, email=%s, password=%s WHERE id=%s", 
                               (name, email, new_password, session['id']))
            else:
                cursor.execute("UPDATE users SET name=%s, email=%s WHERE id=%s", 
                               (name, email, session['id']))
                
            mysql.connection.commit()
            cursor.close()
            
            session['name'] = name
            return redirect(url_for('admin_bp.settings'))
            
        cursor.close()
        return render_template('admin_settings.html', admin_info=admin_info)
        
    return redirect(url_for('login'))