from flask import Flask, redirect, request, render_template_string, render_template

app = Flask(__name__)

# --- CONFIGURATION ---
LINKS_FILE = "links.txt"
SECRET_PIN = "o5Z6u>F7iD9a"  # Change this to your desired PIN
# ---------------------

def get_destinations():
    links = {}
    try:
        with open(LINKS_FILE, "r") as f:
            for line in f:
                if "," in line:
                    name, url = line.strip().split(",", 1)
                    links[name] = url
    except FileNotFoundError:
        open(LINKS_FILE, "a").close() # Create it if it doesn't exist
    return links


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/mkw100")
def mkw100():
    return render_template("100percentMKW.html")

@app.route('/r/<key>')
def reverse_proxy(key):
    data = get_destinations()
    if key in data:
        return redirect(data[key])
    #return f"Shortcut '{key}' not found", 404


@app.route('/add', methods=['GET', 'POST'])
def add_link():
    message = ""
    if request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('url')
        pin = request.form.get('pin')

        if pin == SECRET_PIN:
            if name and url:
                with open(LINKS_FILE, "a") as f:
                    f.write(f"{name},{url}\n")
                message = f"Successfully added {name}!"
            else:
                message = "Please fill in all fields."
        else:
            message = "Incorrect PIN!"

    return render_template_string('''
        <h1>Add Shortcut</h1>
        <p style="color: red;">{{ message }}</p>
        <form method="post">
            Name: <input type="text" name="name" placeholder="Youtube"><br><br>
            URL: <input type="text" name="url" placeholder="https://youtube.com/..."><br><br>
            PIN: <input type="password" name="pin"><br><br>
            <input type="submit" value="Add Link">
        </form>
    ''', message=message)

if __name__ == "__main__":
    app.run(debug=True)