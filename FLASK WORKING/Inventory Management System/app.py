import json  # Ye line sabse zaroori hai standard functions ke liye
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# --- Data Load karne ka sahi tareeka ---
def load_data():
    try:
        with open("inventory.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, Exception): 
        # Agar file nahi hai ya koi aur masla hai, to khali list return hogi
        return []

@app.route('/')
def index():
    inventory = load_data()
    return render_template('index.html', inventory=inventory)

@app.route('/add', methods=['POST'])
def add_item():
    item_name = request.form.get("item_name")
    quantity = request.form.get("quantity")
    
    inventory = load_data()
    
    try:
        qty = int(quantity)
        new_item = {"item": item_name, "qty": qty}
        inventory.append(new_item)
        
        # Save karne ka wahi tarika
        with open("inventory.json", "w") as f:
            json.dump(inventory, f, indent=4)
            
    except ValueError:
        print("Invalid quantity entered!") # Console par nazar aayega
        
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)