from flask import Flask, render_template, redirect, url_for, request, session,flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management

# Admin credentials (used directly in code for simplicity)
ADMIN_USERNAME = 'admin@railway.ac.in'
ADMIN_PASSWORD = '1234'

def get_db_connection():
    conn = sqlite3.connect('railway.db')
    conn.row_factory = sqlite3.Row  # This will allow us to access columns by name
    return conn

@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('home.html', logged_in=True, user_name=session['user_name'])
    return render_template('home.html', logged_in=False)

@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        from_station = request.form['from_station'].lower()
        to_station = request.form['to_station'].lower()
        conn = get_db_connection()
        trains = conn.execute('''
            SELECT * FROM train WHERE LOWER(from_station) = ? AND LOWER(to_station) = ?
        ''', (from_station, to_station)).fetchall()
        conn.close()
        return render_template('search_results.html', trains=trains)
    return render_template('search_form.html')

@app.route('/view_trains')
def view_trains():
    conn = get_db_connection()
    trains = conn.execute('SELECT * FROM train').fetchall()
    conn.close()
    return render_template('view_trains.html', trains=trains)

@app.route('/reserve/<int:train_id>', methods=['GET', 'POST'])
def reserve(train_id):
    conn = get_db_connection()
    train = conn.execute('SELECT * FROM train WHERE train_id = ?', (train_id,)).fetchone()

    if request.method == 'POST':
        no_of_seats = int(request.form['seats'])
        total_amount = train['amount_per_seat'] * no_of_seats
        user_id = session['user_id']  # Get the logged-in user's ID
        
        # Check if enough seats are available
        if no_of_seats > train['available_seats']:
            return "Not enough seats available. Please try again with a smaller number of seats."

        # Insert reservation into the book table
        conn.execute('''
            INSERT INTO book (user_id, train_id, status, no_of_seats, total_amount)
            VALUES (?, ?, 'Booked', ?, ?)
        ''', (user_id, train_id, no_of_seats, total_amount))
        
        # Update the available seats in the train table
        new_available_seats = train['available_seats'] - no_of_seats
        conn.execute('UPDATE train SET available_seats = ? WHERE train_id = ?',
                     (new_available_seats, train_id))
        # Once payment is successful, update the status to 'Paid'
        

        conn.commit()

        # Fetch the reservation status and other details for confirmation
        reservation = conn.execute('SELECT * FROM book WHERE user_id = ? AND train_id = ? ORDER BY book_id DESC LIMIT 1',
                                   (user_id, train_id)).fetchone()
        

        conn.close()

        # Render the confirmation page with status, train, and reservation details
        return render_template('confirmation.html', train=train, seats=no_of_seats, total_amount=total_amount, status=reservation['status'])

    conn.close()
    return render_template('reservation.html', train=train)


@app.route('/reserved_seats')
def reserved_seats():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    user_id = session['user_id']
    conn = get_db_connection()

    # Fetch all bookings for the current user
    reservations = conn.execute('''
        SELECT b.book_id, b.train_id, b.no_of_seats, b.status, t.name as train_name, t.from_station, t.to_station
        FROM book b
        JOIN train t ON b.train_id = t.train_id
        WHERE b.user_id = ?
    ''', (user_id,)).fetchall()

    conn.close()

    return render_template('reserved_seats.html', reservations=reservations)

@app.route('/cancel_reservation/<int:booking_id>', methods=['POST'])
def cancel_reservation(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    user_id = session['user_id']
    conn = get_db_connection()

    # Fetch the booking details to get the train ID and number of seats reserved
    booking = conn.execute('SELECT * FROM book WHERE book_id = ? AND user_id = ?', 
                           (booking_id, user_id)).fetchone()

    if booking is None:
        flash('Booking not found or you do not have permission to cancel it.')
        return redirect(url_for('reserved_seats'))

    train_id = booking['train_id']
    no_of_seats = booking['no_of_seats']

    # Update the booking status to 'Cancelled'
    conn.execute('UPDATE book SET status = "Cancelled" WHERE book_id = ?', (booking_id,))
    
    # Fetch the train details to update the available seats
    train = conn.execute('''
        SELECT `train_id`, `name`, `from_station`, `to_station`, `depart_time`, `available_seats`, `amount_per_seat`
        FROM train
        WHERE `train_id` = ?
    ''', (train_id,)).fetchone()

    if train is None:
        flash('Train not found.')
        return redirect(url_for('reserved_seats'))

    new_available_seats = train['available_seats'] + no_of_seats

    # Update the train table to reflect the available seats after cancellation
    conn.execute('UPDATE train SET available_seats = ? WHERE train_id = ?', 
                 (new_available_seats, train_id))

    conn.commit()
    conn.close()

    flash('Your reservation has been successfully cancelled.')
    return redirect(url_for('reserved_seats'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Check if the email already exists in the database
        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()
        
        if existing_user:
            return render_template('register.html', error="Email already registered.")
        
        # If email is unique, insert the new user into the database
        conn.execute('INSERT INTO user (name, email, password) VALUES (?, ?, ?)', (name, email, password))
        conn.commit()
        conn.close()
        
        # Redirect to the login page after successful registration
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if login is for admin
        if email == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Login successful! Welcome to the Admin Dashboard.', 'success')
            return redirect(url_for('admin_dashboard'))
        
        # Check if login is for a regular user
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and user['password'] == password:
            session['user_id'] = user['user_id']
            session['user_name'] = user['name']
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('admin', None)  # Remove admin session
    return redirect(url_for('home'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        flash('You must log in to access the admin dashboard.', 'danger')
        return redirect(url_for('login'))
    
    # Any success flash message
    flash('Welcome back to the Admin Dashboard!', 'success')
    
    return render_template('admin_dashboard.html')
@app.route('/add_train', methods=['GET', 'POST'])
def add_train():
    if 'admin_logged_in' not in session:
        flash('You must log in to add a train.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        from_station = request.form['from_station']
        to_station = request.form['to_station']
        depart_time = request.form['depart_time']
        available_seats = request.form['available_seats']
        amount_per_seat = request.form['amount_per_seat']

        # Validate fields
        if not name or not from_station or not to_station or not depart_time:
            flash('All fields are required.', 'danger')
        else:
            # Assuming train is successfully added to the database
            conn = sqlite3.connect('railway.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO train (name, from_station, to_station, depart_time, available_seats, amount_per_seat)
                VALUES (?, ?, ?, ?, ?, ?)''', (name, from_station, to_station, depart_time, available_seats, amount_per_seat))
            conn.commit()
            conn.close()
            
            flash('Train added successfully!', 'success')
            return redirect(url_for('view_train_schedule'))

    return render_template('add_train.html')

@app.route('/view_train_schedule')
def view_train_schedule():
    if 'admin_logged_in' not in session:
        flash('You must log in to view the train schedule.', 'danger')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('railway.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM train')
    trains = cursor.fetchall()  # Fetch all train records
    conn.close()

    return render_template('view_train_schedule.html', trains=trains)



@app.route('/delete_train/<int:train_id>', methods=['GET'])
def delete_train(train_id):
    if 'admin_logged_in' not in session:
        flash('You must log in to delete a train.', 'danger')
        return redirect(url_for('login'))

    conn = sqlite3.connect('railway.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM train WHERE train_id = ?', (train_id,))
    conn.commit()
    conn.close()

    flash('Train deleted successfully!', 'success')
    return redirect(url_for('view_train_schedule'))

@app.route('/view_users')
def view_users():
    if 'admin_logged_in' not in session:
        flash('You must log in to view users.', 'danger')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('railway.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    conn.close()

    return render_template('view_users.html', users=users)

@app.route('/delete_user/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    if 'admin_logged_in' not in session:
        flash('You must log in to delete a user.', 'danger')
        return redirect(url_for('login'))

    conn = sqlite3.connect('railway.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

    flash('User deleted successfully!', 'success')
    return redirect(url_for('view_users'))



if __name__ == '__main__':
    app.run(debug=True)

