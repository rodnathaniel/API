from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql.cursors
import re


app = Flask(__name__)

app.secret_key = 'a0ad259a8fbee24b73d496dde1dfc120'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_users'

mysql = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB'],
    cursorclass=pymysql.cursors.DictCursor
)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'email' in session:
        return redirect(url_for('manage_students'))

    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password,))
        user = cursor.fetchone()
        if user:
            session['email'] = user['email']
            flash('Logged in successfully!', 'success')
            print("User logged in successfully")
            return redirect(url_for('manage_students'))
        else:
            message = 'Please enter correct email / password!'
            print("Login failed")
    return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            message = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not userName or not password or not email:
            message = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)', (userName, email, password))
            mysql.commit()
            message = 'You have successfully registered!'
            flash(message, 'success')
    elif request.method == 'POST':
        message = 'Please fill out the form!'
    return render_template('register.html', message=message)

@app.route('/user', methods=['GET', 'POST'])
def manage_students():
    if 'email' not in session:
        return redirect(url_for('login'))

    cursor = mysql.cursor()

    if request.method == 'POST':
        student_name = request.form['student_name']
        student_number = request.form['student_number']
        student_birthday = request.form['student_birthday']

        cursor.execute('INSERT INTO students (name, student_number, birthday) VALUES (%s, %s, %s)',
                       (student_name, student_number, student_birthday))
        mysql.commit()
        flash('Student added successfully', 'success')

    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    return render_template('user.html', students=students)

@app.route('/user/update/<int:student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    if 'email' not in session:
        return redirect(url_for('login'))

    cursor = mysql.cursor()
    cursor.execute('SELECT * FROM students WHERE id = %s', (student_id,))
    student = cursor.fetchone()

    if request.method == 'POST':
        student_name = request.form['edited_name']
        student_number = request.form['edited_student_number']
        student_birthday = request.form['edited_birthday']

        cursor.execute('UPDATE students SET name = %s, student_number = %s, birthday = %s WHERE id = %s',
                       (student_name, student_number, student_birthday, student_id))
        mysql.commit()
        flash('Student updated successfully', 'success')

        return redirect(url_for('manage_students'))

@app.route('/user/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if 'email' not in session:
        return redirect(url_for('login'))

    cursor = mysql.cursor()
    cursor.execute('DELETE FROM students WHERE id = %s', (student_id,))
    mysql.commit()
    flash('Student deleted successfully', 'success')

    return redirect(url_for('manage_students'))

if __name__ == "__main__":
    app.run(debug=True)
