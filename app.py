from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

#Create database and set up the table
def init_db():
    conn = sqlite3.connect('database.db')
    conn.execute("TBD")
    conn.close()

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Route to display form to add a new habit
@app.route('/add')
def add_habit_form():
    return render_template('add_habit.html')

# Route to handle form submission for new habit
@app.route('/add_habit', methods=['POST'])
def add_habit():
    habit_name = request.form['habit_name']
    goal = request.form['goal']
    conn = sqlite3.connect('database.db')
    conn.execute("INSERT INTO habits (name, goal) VALUES (?, ?)", (habit_name, goal))
    conn.commit()
    conn.close()
    return redirect('/progress')

# Track route - Spreadsheet breakdown of tasks (Placeholder)
@app.route('/track')
def track():
    # You can customize this later with dynamic content from the database
    return render_template('track.html')

# Route to show progress - show list of habits and goals
@app.route('/progress')
def progress():
    conn = sqlite3.connect('database.db')
    cursor = conn.execute("SELECT * FROM habits")
    habits = cursor.fetchall()
    conn.close()
    return render_template('progress.html', habits=habits)

# Contact route
@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
