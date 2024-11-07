from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def dashboard():
    # Load the CSV data
    csv_file = 'interface_summary_live_FWTX2v3.csv'
    try:
        data = pd.read_csv(csv_file, parse_dates=['Timestamp'])
    except FileNotFoundError:
        data = pd.DataFrame()  # Empty DataFrame if file not found

    # Pass the data to the template
    return render_template('dashboard.html', tables=[data.to_html(classes='data', header="true")])

if __name__ == '__main__':
    app.run(debug=True)