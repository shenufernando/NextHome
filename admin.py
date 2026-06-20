from flask import Blueprint, render_template, session, redirect, url_for, request, flash
import MySQLdb.cursors

admin_bp = Blueprint('admin_bp', __name__)

# --- 1. ADMIN DASHBOARD ---
@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'loggedin' in session and session['role'] == 'admin':
        from app import mysql
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # new user 5 
        cursor.execute('SELECT id, name, email, role FROM users ORDER BY id DESC LIMIT 5')
        users = cursor.fetchall()

        # total users
        cursor.execute('SELECT COUNT(*) as count FROM users')
        user_count = cursor.fetchone()['count']
        
        # total Properties
        cursor.execute('SELECT COUNT(*) as count FROM properties')
        property_count = cursor.fetchone()['count']
        
        # Basic (pending) ස, Premium (Pending_Approval) 
        cursor.execute("SELECT * FROM properties WHERE status IN ('pending', 'Pending_Approval') ORDER BY id DESC")
        pending_properties = cursor.fetchall()
        
        cursor.close()

        return render_template('admin_dashboard.html', 
                               users=users, 
                               user_count=user_count, 
                               property_count=property_count,
                               pending_properties=pending_properties)
    
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


# =======================================================
# 🏢 ADMIN PROPERTIES MANAGEMENT (FIXED & LOGGED IN CHECKED)
# =======================================================

# --- 1. VIEW ALL PROPERTIES & STATS ---
@admin_bp.route('/admin/properties')
def admin_properties():
    if 'loggedin' in session and session['role'] == 'admin':
        from app import mysql
        cursor = mysql.connection.cursor()
        
        # 📊 
        cursor.execute("SELECT COUNT(*) FROM properties WHERE status = 'Approved'")
        active_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM properties WHERE status = 'Rejected'")
        reject_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM properties WHERE status IN ('pending', 'Pending_Approval')")
        pending_count = cursor.fetchone()[0]

        # 📋 
        sql = """SELECT p.id, p.title, p.price, p.type, p.status, p.expiry_date, p.image_url, u.name 
                 FROM properties p 
                 JOIN users u ON p.seller_id = u.id 
                 ORDER BY p.id DESC"""
        cursor.execute(sql)
        
        columns = [col[0] for col in cursor.description]
        properties = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.close()
        
        return render_template('admin_property.html', 
                               properties=properties, 
                               active_count=active_count, 
                               reject_count=reject_count, 
                               pending_count=pending_count)
                               
    return redirect(url_for('login'))


# --- 2. APPROVE PROPERTY ROUTE ---

# --- 2. APPROVE PROPERTY ROUTE (Fixed for Premium Payment Workflow) ---
@admin_bp.route('/admin/property/approve/<int:property_id>', methods=['POST'])
def approve_property(property_id):
    if 'loggedin' in session and session['role'] == 'admin':
        from app import mysql
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # check Basic , Premium 
        cursor.execute("SELECT plan FROM properties WHERE id = %s", (property_id,))
        property_data = cursor.fetchone()
        
        if property_data:
            # Premium , Approve ක
            if property_data['plan'] == 'premium':
                new_status = 'Approved_Pending_Payment'
                flash_msg = 'Premium Property approved! Waiting for seller payment.'
            else:
                new_status = 'Approved'
                flash_msg = 'Basic Property approved successfully and now Live!'
                
            cursor.execute("UPDATE properties SET status = %s WHERE id = %s", (new_status, property_id))
            mysql.connection.commit()
            
        cursor.close()
        flash(flash_msg, 'success')
        return redirect(url_for('admin_bp.admin_properties'))
        
    return redirect(url_for('login'))


# --- 3. REJECT PROPERTY ROUTE ---
@admin_bp.route('/admin/property/reject/<int:property_id>', methods=['POST'])
def reject_property(property_id):
    if 'loggedin' in session and session['role'] == 'admin':
        from app import mysql
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE properties SET status = 'Rejected' WHERE id = %s", (property_id,))
        mysql.connection.commit()
        cursor.close()
        flash('Property rejected successfully!', 'danger')
        return redirect(url_for('admin_bp.admin_properties'))
        
    return redirect(url_for('login'))


# --- 4. DELETE PROPERTY ROUTE ---
@admin_bp.route('/admin/property/delete/<int:property_id>', methods=['POST'])
def delete_property(property_id):
    if 'loggedin' in session and session['role'] == 'admin':
        from app import mysql
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM properties WHERE id = %s", (property_id,))
        mysql.connection.commit()
        cursor.close()
        flash('Property deleted from system!', 'warning')
        return redirect(url_for('admin_bp.admin_properties'))
        
    return redirect(url_for('login'))



@admin_bp.route('/admin_earnings') 
def admin_earnings():
    if 'loggedin' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
        
    #   Circular Import error 
    from app import mysql
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        # 1. Approved(Basic)
        cursor.execute("SELECT COUNT(*) AS total FROM properties WHERE plan = 'basic' AND status = 'approved'")
        basic_count = cursor.fetchone()['total']
        
        # 2. Approved (Premium)
        cursor.execute("SELECT COUNT(*) AS total FROM properties WHERE plan = 'premium' AND status = 'approved'")
        premium_count = cursor.fetchone()['total']
        
        # 3. Payments (SUM)
        cursor.execute("SELECT SUM(amount) AS total_earnings FROM payments WHERE payment_status = 'completed'")
        earnings_result = cursor.fetchone()
        total_earnings = earnings_result['total_earnings'] if earnings_result['total_earnings'] is not None else 0.00
        
        # 4. \\ payments \
        cursor.execute("SELECT id, property_id, seller_id, amount, payment_status, paid_at FROM payments ORDER BY id DESC")
        payments_list = cursor.fetchall()
        
    except Exception as e:
        print(f"Error: {e}")
        basic_count = 0
        premium_count = 0
        total_earnings = 0.00
        payments_list = []
    finally:
        cursor.close()
    
    return render_template('admin_earnings.html', 
                           basic_count=basic_count, 
                           premium_count=premium_count, 
                           total_earnings=total_earnings,
                           payments=payments_list)