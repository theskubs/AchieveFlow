# app.py
from flask import Flask, render_template, request, redirect, send_file
import csv
import os
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO
import base64
import logging

app = Flask(__name__)
app.secret_key = 'secret_key'

# File paths
data_file = 'data.csv'
users_file = 'users.csv'

# Initialize CSV files
def init_csv():
    if not os.path.exists(data_file):
        with open(data_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['user', 'habit', 'goal', 'completed', 'date', 'frequency'])  # Headers

    if not os.path.exists(users_file):
        with open(users_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'password'])  # Headers

@app.route('/')
def index():
    return render_template('index.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if user exists
        with open(users_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if row[0] == username and row[1] == password:
                    session['user'] = username
                    flash(f'Welcome back, {username}!')
                    return redirect('/track')
        flash('Invalid username or password.')
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.')
    return redirect('/')

# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Add user to users file
        with open(users_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([username, password])
        flash('Registration successful. Please log in.')
        return redirect('/login')
    return render_template('register.html')

# Add habit
@app.route('/add_habit', methods=['GET', 'POST'])
def add_habit():
    if 'user' not in session:
        flash('You must be logged in to add a habit.')
        return redirect('/login')

    if request.method == 'POST':
        habit_name = request.form['habit_name']
        goal = request.form['goal']
        frequency = request.form['frequency']
        completed = 0
        date = datetime.now().strftime('%Y-%m-%d')

        with open(data_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([session['user'], habit_name, goal, completed, date, frequency])
        flash('Habit added successfully!')
        return redirect('/track')
    return render_template('add_habit.html')

# Track habits
@app.route('/track')
def track():
    if 'user' not in session:
        flash('You must be logged in to track habits.')
        return redirect('/login')

    habits = []
    with open(data_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if row[0] == session['user']:
                habits.append(row)
    return render_template('track.html', habits=habits)

# Mark habit as completed
@app.route('/mark_habit_completed', methods=['POST'])
def mark_habit_completed():
    habit_name = request.form['habit_name']
    updated_rows = []
    updated = False

    with open(data_file, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            if row[0] == session['user'] and row[1] == habit_name:
                row[3] = str(int(row[3]) + 1)
                updated = True
            updated_rows.append(row)

    if updated:
        with open(data_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(updated_rows)
        flash(f'Habit "{habit_name}" marked as completed.')
    else:
        flash('Failed to mark habit as completed.')

    return redirect('/track')

# Progress data for Chart.js
@app.route('/progress-data')
def progress_data():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    habits = []
    completed = []
    dates = []

    with open(data_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if row[0] == session['user']:
                habits.append(row[1])
                completed.append(int(row[3]))
                dates.append(row[4])

    return jsonify({'habits': habits, 'completed': completed, 'dates': dates})

# Download CSV
@app.route('/download_csv')
def download_csv():
    if 'user' not in session:
        flash('You must be logged in to download data.')
        return redirect('/login')

    filtered_rows = []
    with open(data_file, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            if row[0] == session['user']:
                filtered_rows.append(row)

    output_file = f'{session["user"]}_habits.csv'
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(filtered_rows)

    return send_file(output_file, as_attachment=True)

if __name__ == '__main__':
    init_csv()
    app.run(debug=True)


