import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, url_for
from mysql.connector import connect, Error
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    print("Attempting to connect to database...")
    try:
        connection = connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password = app.config['MYSQL_PASSWORD'],
            database = app.config['MYSQL_DB']
        )
        print("Database connection successful")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def index():
    print("Index route accessed")
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('index.html', students=students)
    else:
        return "Database connection error"

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    print("Add student route accessed")
    if request.method == 'POST':
        name = request.form['name']
        roll_number = request.form['roll_number']
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO students (name, roll_number) VALUES (%s, %s)", (name, roll_number))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('index'))
    return render_template('add_student.html')

@app.route('/delete_student', methods=['GET', 'POST'])
def delete_student():
    if request.method == 'POST':
        roll_number = request.form['roll_number']
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            # Get the student_id for the given roll_number
            cursor.execute("SELECT id FROM students WHERE roll_number = %s", (roll_number,))
            student = cursor.fetchone()
            if student:
                student_id = student[0]
                # Delete related attendance records
                cursor.execute("DELETE FROM attendance WHERE student_id = %s", (student_id,))
                # Delete the student record
                cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
                connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('index'))
    return render_template('delete_student.html')


@app.route('/mark_attendance', methods=['GET', 'POST'])
def mark_attendance():
    print("Mark attendance route accessed")
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        if request.method == 'POST':
            student_id = request.form['student_id']
            date = request.form['date']
            status = request.form['status']
            cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, %s)", (student_id, date, status))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('index'))
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('mark_attendance.html', students=students)
    else:
        return "Database connection error"
    
@app.route('/view_attendance', methods=['GET'])
def view_attendance():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT students.name, students.roll_number, attendance.date, attendance.status FROM attendance INNER JOIN students ON attendance.student_id = students.id")
        attendance_records = cursor.fetchall()
        cursor.close()
        connection.close()
    return render_template('view_attendance.html', attendance_records=attendance_records)

if __name__ == '__main__':
    print("Starting Flask app")
    app.run(debug=True, port=5001)
