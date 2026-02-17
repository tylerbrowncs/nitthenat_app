import requests
import csv
from flask import Flask, redirect

app = Flask(__name__)

# Replace this with your "Publish to Web" CSV URL
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT4g-5ONfHBYKFbAP4YFRMzqeok-2CAsSgvf-40gwrwnGlz2E06-Sxxp752D84emLak-zKtFvv3IDye/pub?output=csv"

def get_destinations():
    links = {}
    try:
        response = requests.get(SHEET_CSV_URL)
        # Decode the CSV data from the web
        decoded_content = response.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        for row in cr:
            if len(row) >= 2:
                # row[0] is shortcut, row[1] is URL
                links[row[0].strip()] = row[1].strip()
    except Exception as e:
        print(f"Error fetching sheet: {e}")
    return links

@app.route('/')
def home():
	return "<h1>NitTheNat</h1>"

@app.route('/r/<key>')
def reverse_proxy(key):
    data = get_destinations()
    
    # Check for the key (case sensitive!)
    if key in data:
        return redirect(data[key])
    
    return f"Shortcut '{key}' not found in {list(data.keys())}", 404

if __name__ == "__main__":
	app.run(host="0.0.0.0")


