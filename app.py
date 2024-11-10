from flask import Flask, render_template, request, redirect, send_file
import csv
import os
import matplotlib.pyplot as plt
from datetime import datetime

app = Flask(__name__)

# Path to the CSV data file
data_file = 'data.csv'

# Initialize the CSV file if it doesn't exist, with headers
def init_csv():
    if not os.path.exists(data_file):
        with open(data_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['habit', 'goal', 'completed', 'date'])  # Headers for CSV file

# Route to add a new habit (GET shows the form, POST handles form submission)
@app.route('/add_habit', methods=['GET', 'POST'])
def add_habit():
    if request.method == 'POST':
        habit_name = request.form['habit-name']
        goal = request.form['habit-goal']
        completed = 0  # Default completed value for a new habit
        date = datetime.now().strftime('%Y-%m-%d')  # Current date for the entry

        # Append the new habit data to the CSV file
        with open(data_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([habit_name, goal, completed, date])

        return redirect('/track')  # Redirect to the tracking page
    return render_template('add_habit.html')  # Render the add habit form

# Route to display the habit data in a table and provide CSV download link
@app.route('/track')
def track():
    habits = []
    # Read the CSV data and store it in a list for rendering
    with open(data_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        habits = list(reader)
    return render_template('track.html', habits=habits)

# Route to download the CSV file directly
@app.route('/download_csv')
def download_csv():
    return send_file(data_file, as_attachment=True, mimetype='text/csv', download_name='habits.csv')

# Route to generate and display the progress chart
@app.route('/progress')
def progress():
    dates = []
    completed_counts = []

    # Read CSV data to get dates and completed counts for chart generation
    with open(data_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            dates.append(row[3])  # Date
            completed_counts.append(int(row[2]))  # Completed count

    # Generate the chart with Matplotlib
    plt.figure(figsize=(10, 5))
    plt.plot(dates, completed_counts, marker='o', color='#139E1C')
    plt.title("Habit Progress Over Time")
    plt.xlabel("Date")
    plt.ylabel("Completed")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the chart as an image in the static folder for display
    chart_path = os.path.join('static', 'progress_chart.png')
    plt.savefig(chart_path)
    plt.close()

    # Render the progress page, which displays the saved chart image
    return render_template('progress.html')

# Main entry point, initialize the CSV file and start the Flask app
if __name__ == '__main__':
    init_csv()  # Ensure CSV file is ready
    app.run(debug=True)  # Run the Flask app in debug mode

