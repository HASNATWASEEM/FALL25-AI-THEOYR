from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)

MESSAGE_FILE = "messages.json"
VISITOR_FILE = "visitors.json"

# Create files if not exist
for file in [MESSAGE_FILE, VISITOR_FILE]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)

projects = [
    {
        "title": "Landing Page",
        "category": "frontend",
        "desc": "Responsive HTML/CSS landing page",
        "img": "/static/images/project1.jpg"
    },
    {
        "title": "Flask Task Manager",
        "category": "backend",
        "desc": "Task manager built with Flask",
        "img": "/static/images/project2.jpg"
    },
    {
        "title": "ML Predictor",
        "category": "ml",
        "desc": "Machine learning model using Pandas & NumPy",
        "img": "/static/images/project3.jpg"
    }
]

@app.route("/", methods=["GET", "POST"])
def index():

    # visitor counter
    with open(VISITOR_FILE, "r") as f:
        visitors = json.load(f)

    visitors.append({"visit": "1"})

    with open(VISITOR_FILE, "w") as f:
        json.dump(visitors, f)

    visitor_count = len(visitors)

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        if name and email and message:

            with open(MESSAGE_FILE, "r") as f:
                data = json.load(f)

            data.append({
                "name": name,
                "email": email,
                "message": message
            })

            with open(MESSAGE_FILE, "w") as f:
                json.dump(data, f, indent=4)

        return redirect(url_for("index"))

    return render_template("index.html",
                           projects=projects,
                           visitors=visitor_count)


@app.route("/admin")
def admin():

    with open(MESSAGE_FILE, "r") as f:
        messages = json.load(f)

    return render_template("admin.html", messages=messages)


@app.route("/api/messages")
def api_messages():

    with open(MESSAGE_FILE, "r") as f:
        data = json.load(f)

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)