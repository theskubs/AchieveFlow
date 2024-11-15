# app.py
from flask import Flask, render_template, request, redirect, send_file
import csv
import os
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO
import base64

app = Flask(__name__)

# Sample data
data_file = 'data.csv'

# Initialize data file
def init_csv():
    if not os.path.exists(data_file):
        with open(data_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['habit', 'goal', 'completed', 'date'])  # Headers for CSV file

@app.route('/')
def index():
    return render_template('index.html')

# Route to add a habit
@app.route('/add_habit', methods=['GET', 'POST'])
def add_habit():
    if request.method == 'POST':
        habit_name = request.form['habit-name']
        goal = request.form['habit-goal']
        completed = 0  # Default completed value for a new habit
        date = datetime.now().strftime('%Y-%m-%d')  # Current date

        # Append data to CSV
        with open(data_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([habit_name, goal, completed, date])
            
        return redirect('/track')  # Redirect to the track page
    return render_template('add_habit.html')

# Consolidated Route for displaying habits and generating the chart
@app.route('/track')
def track():
    habits = []
    dates = []
    completed_counts = []

    # Read data from the CSV file
    if os.path.exists(data_file):
        with open(data_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                habits.append(row)
                dates.append(row[3])
                completed_counts.append(int(row[2]))

    # Generate a bar chart for habit completion
    if completed_counts:
        plt.figure(figsize=(10, 5))
        plt.bar(dates, completed_counts, color='#139E1C')
        plt.title('Habit Completion Over Time')
        plt.xlabel('Date')
        plt.ylabel('Completed')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save chart as Base64
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        chart_img_data = base64.b64encode(img.getvalue()).decode('utf-8')
    else:
        chart_img_data = None

    return render_template('track.html', habits=habits, chart_img_data=chart_img_data)

# Route to download the CSV file
@app.route('/download_csv')
def download_csv():
    return send_file(data_file, as_attachment=True, mimetype='text/csv', download_name='habits.csv')

# Route to dynamically generate and display the progress chart
@app.route('/progress')
def progress():
    habits = []
    dates = []
    completed_counts = []

    # Read CSV data
    if os.path.exists(data_file):
        with open(data_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                habits.append(row[0])
                completed_counts.append(int(row[2]))
                dates.append(row[3])

    # Generate chart
    plt.figure(figsize=(10, 5))
    plt.plot(dates, completed_counts, marker='o', color='#139E1C')
    plt.title("Habit Progress Over Time")
    plt.xlabel("Date")
    plt.ylabel("Completed")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save chart to a BytesIO stream
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    # Encode image to base64 to display inline
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    return render_template('progress.html', img_data=img_base64)

# Route for the contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    init_csv()
    app.run(debug=True)



