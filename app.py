from flask import Flask, redirect, abort
import os, json
app = Flask(__name__)

def get_destinations():
    # This finds the folder app.py is in, then goes one level up
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)
    json_path = os.path.join(parent_dir, 'shortcut_data.json')
    
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {json_path}")
        return {}

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


