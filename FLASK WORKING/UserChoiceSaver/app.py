from flask import Flask, render_template, request, json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html') # Pehle user ko form dikhao

@app.route('/submit', methods=['POST'])
def save_data():
    # --- YAHAN AAPKA CODE START HOTA HAI ---
    
    # input() ki jagah hum request.form use karte hain
    user_favclr = request.form.get("color") 
    user_age = request.form.get("age")

    filename = "user_choice.json"
    data_to_save = {
        "favorite_color": user_favclr,
        "age": user_age
    }

    try:
        with open(filename, "w") as f:
            json.dump(data_to_save, f, indent=4)
        return f"<h1>Mubarak ho! {user_favclr} save ho gaya!</h1>"
    
    except Exception as e:
        return f"<h1>Kuch masla hua: {e}</h1>"
    
    # --- YAHAN AAPKA CODE KHATAM ---

if __name__ == '__main__':
    app.run(debug=True)