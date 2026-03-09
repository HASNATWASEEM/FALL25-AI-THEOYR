import json, os, io
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort, send_file, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from collections import Counter

# PDF Libraries
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config['SECRET_KEY'] = 'IPS_PAKISTAN_KEY_786'

# --- Login Manager Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Helper Functions for JSON ---
def load_json(filename):
    if not os.path.exists(filename): return []
    try:
        with open(filename, "r") as f: return json.load(f)
    except: return []

def save_json(filename, data):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

# --- PDF RECEIPT GENERATOR ---
def generate_receipt_pdf(customer_name, item_name, qty, sale_price):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=(300, 480))
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(150, 450, "IPS INVENTORY SYSTEM")
    p.setFont("Helvetica", 8)
    p.drawCentredString(150, 438, "Official Receipt - Karachi")
    p.line(20, 420, 280, 420)
    bill_no = datetime.now().strftime("%y%m%d%H%M")
    p.setFont("Helvetica-Bold", 9)
    p.drawString(30, 405, f"Bill No: #{bill_no}")
    p.setFont("Helvetica", 9)
    p.drawString(30, 392, f"Date: {datetime.now().strftime('%d-%m-%Y %I:%M %p')}")
    p.drawString(30, 379, f"Customer: {customer_name if customer_name else 'Walking Customer'}")
    p.line(20, 370, 280, 370)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(30, 355, "Item Description")
    p.drawRightString(200, 355, "Qty")
    p.drawRightString(270, 355, "Total")
    p.setFont("Helvetica", 9)
    p.drawString(30, 335, f"{item_name[:22]}")
    p.drawRightString(200, 335, f"{qty}")
    total_val = float(sale_price) * int(qty)
    p.drawRightString(270, 335, f"{total_val:,.0f}")
    p.line(20, 320, 280, 320)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(30, 300, "NET AMOUNT:")
    p.drawRightString(270, 300, f"Rs. {total_val:,.0f}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- SALES TRACKER ---
def log_sale(item_name, qty, sale_price, cost_price):
    sales = load_json("sales.json")
    profit_per_unit = float(sale_price) - float(cost_price)
    total_profit = profit_per_unit * int(qty)
    sales.append({
        "item": item_name,
        "qty": int(qty),
        "amount": float(sale_price) * int(qty),
        "profit": total_profit,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "month": datetime.now().strftime("%Y-%m"),
        "time": datetime.now().strftime("%I:%M %p")
    })
    save_json("sales.json", sales)

# --- ACTIVITY LOGGER ---
def log_activity(username, action):
    logs = load_json("logs.json")
    logs.append({
        "user": username,
        "action": action,
        "time": datetime.now().strftime("%Y-%m-%d %I:%M %p")
    })
    save_json("logs.json", logs)

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    users = load_json("users.json")
    for u in users:
        if u['id'] == user_id:
            return User(u['id'], u['username'], u.get('role', 'Staff'))
    return None

# --- AUTH ROUTES ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        users = load_json("users.json")
        if any(u['username'] == username for u in users):
            return "Username exists! <a href='/signup'>Try again</a>"
        new_user = {"id": str(len(users) + 1), "username": username, "password": generate_password_hash(password), "role": role}
        users.append(new_user)
        save_json("users.json", users)
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = load_json("users.json")
        for u in users:
            if u['username'] == username and check_password_hash(u['password'], password):
                user_obj = User(u['id'], u['username'], u.get('role', 'Staff'))
                login_user(user_obj)
                return redirect(url_for('index'))
        return "WRONG CREDENTIALS <a href='/login'>Try again</a>"
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    log_activity(current_user.username, "Logged Out")
    logout_user()
    session.clear()
    return redirect(url_for('login'))

# --- INVENTORY & REPORTS ROUTES ---

@app.route('/')
@login_required
def index():
    query = request.args.get('query', '').lower()
    inventory = load_json("inventory.json")
    sales = load_json("sales.json")
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_profit = sum(s['profit'] for s in sales if s['date'] == today_str)
    
    loss_items = []
    total_potential_loss = 0
    for item in inventory:
        if float(item['sale']) < float(item['cost']):
            loss_per_unit = float(item['cost']) - float(item['sale'])
            p_loss = loss_per_unit * int(item['qty'])
            loss_items.append({
                "name": item['item'],
                "loss_per_unit": loss_per_unit,
                "total_loss": p_loss
            })
            total_potential_loss += p_loss

    item_counts = Counter()
    for s in sales:
        item_counts[s['item']] += s['qty']
    best_seller = item_counts.most_common(1)[0] if item_counts else ("None", 0)

    if query:
        inventory = [item for item in inventory if query in item['item'].lower() or query == item.get('barcode','')]
    
    return render_template('index.html', inventory=inventory, username=current_user.username, 
                           role=current_user.role, today_profit=today_profit, 
                           best_seller=best_seller, loss_items=loss_items, 
                           total_potential_loss=total_potential_loss)

# --- ADD ITEM (FIXED) ---
@app.route('/add', methods=['POST'])
@login_required
def add_item():
    if current_user.role != 'Manager': return "Access Denied!", 403
    item_name = request.form.get("item_name").strip()
    barcode = request.form.get("barcode", "").strip()
    quantity = int(request.form.get("quantity"))
    cost_price = float(request.form.get("cost_price"))
    sale_price = float(request.form.get("sale_price"))
    
    inventory = load_json("inventory.json")
    item_found = False
    for item in inventory:
        if (barcode and item.get('barcode') == barcode) or (item['item'].lower() == item_name.lower()):
            item['qty'] += quantity
            item['cost'] = cost_price
            item['sale'] = sale_price
            if barcode: item['barcode'] = barcode
            item_found = True
            break
    
    if not item_found:
        inventory.append({"item": item_name, "barcode": barcode, "qty": quantity, "cost": cost_price, "sale": sale_price})
    
    save_json("inventory.json", inventory)
    log_activity(current_user.username, f"Added Stock: {item_name}")
    return redirect(url_for('index'))

# --- SELL ITEM ---
@app.route('/sell/<int:item_id>', methods=['POST'])
@login_required
def sell_item(item_id):
    qty_sold = int(request.form.get("qty_sold", 0))
    cust_name = request.form.get("customer_name", "Walking Customer").strip()
    wants_slip = request.form.get("print_receipt")
    inventory = load_json("inventory.json")
    
    if 0 <= item_id < len(inventory):
        item = inventory[item_id]
        if item['qty'] >= qty_sold and qty_sold > 0:
            item['qty'] -= qty_sold
            log_sale(item['item'], qty_sold, item['sale'], item['cost'])
            save_json("inventory.json", inventory)
            
            if wants_slip:
                pdf_buffer = generate_receipt_pdf(cust_name, item['item'], qty_sold, item['sale'])
                return send_file(pdf_buffer, as_attachment=True, download_name=f"Slip_{item['item']}.pdf", mimetype='application/pdf')
    return redirect(url_for('index'))

# --- BARCODE SCANNER API ---
@app.route('/get_item_by_barcode/<barcode>')
@login_required
def get_item_by_barcode(barcode):
    inventory = load_json("inventory.json")
    for index, item in enumerate(inventory):
        if item.get('barcode') == barcode:
            return jsonify({"success": True, "id": index, "item": item})
    return jsonify({"success": False})

@app.route('/logs')
@login_required
def view_logs():
    if current_user.role != 'Manager': return "Unauthorized", 403
    logs = load_json("logs.json")
    return render_template('logs.html', logs=list(reversed(logs)))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)