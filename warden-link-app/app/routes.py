from flask import render_template, redirect, url_for, request, session
import hashlib
import json
import os
from functools import lru_cache

from app import app

from balance.check_balance import get_balance
from validate.validation import is_valid_xrp_address
from balance.convertation import get_xrp_price
from balance.rounding import round_down_4
from qr.generate_qr import generate_xrp_qr
from transaction.create_transaction import save_unsigned_transaction
from transaction.send_transaction import send_signed_tx_from_data

DATA_FILE = "user.json"

@lru_cache(maxsize=128)
def get_balance_cached(address):
    return get_balance(address)

def load_user_address():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f).get('address')
    return None

@app.route('/')
def index():
    address = load_user_address()

    if address:
        with open(DATA_FILE, "r") as f:
            user_data = json.load(f)

        if "pincode" in user_data:
            return redirect(url_for("enterpin"))
        else:
            return redirect(url_for("setpin"))

    return render_template("index.html")


@app.route('/enter', methods=['GET', 'POST'])
def enter():
    if request.method == 'POST':
        address = request.form.get('address')
        if is_valid_xrp_address(address):
            with open('user.json', 'w') as f:
                json.dump({'address': address, "output_path": os.path.expanduser("~")}, f)
            return redirect('/setpin')
        else:
            return render_template('enter.html')
    return render_template('enter.html')

@app.route("/setpin", methods=["GET", "POST"])
def setpin():
    
    with open(DATA_FILE, "r") as f:
        user_data = json.load(f)

    if "pincode" in user_data:
        return redirect(url_for("enterpin"))

    if request.method == "POST":
        pincode = request.form.get("pincode", "")
        if pincode.isdigit() and len(pincode) == 4:
            hashed_pin = hashlib.sha256(pincode.encode()).hexdigest()
            user_data["pincode"] = hashed_pin
            with open(DATA_FILE, "w") as f:
                json.dump(user_data, f)
            return redirect(url_for("enterpin"))

    return render_template("setpin.html")

@app.route("/enterpin", methods=["GET", "POST"])
def enterpin():
    with open(DATA_FILE, "r") as f:
        user_data = json.load(f)

    if request.method == "POST":
        pincode = request.form.get("pincode", "")
        if pincode.isdigit() and len(pincode) == 4:
            hashed_pin = hashlib.sha256(pincode.encode()).hexdigest()
            if user_data.get("pincode") == hashed_pin:
                session['authenticated'] = True
                return redirect(url_for("portfolio"))
        return render_template("enterpin.html", error=True)

    return render_template("enterpin.html")

@app.route("/update_balance")
def update_balance():
    with open("user.json", "r") as f:
        user_data = json.load(f)

    address = user_data.get("address", "")
    if not address:
        return {"balance": 0.0}

    balance = get_xrp_price(get_balance_cached(address)-1)
    round_balance = round(balance, 2)

    user_data["last_balance"] = round_balance

    with open("user.json", "w") as f:
        json.dump(user_data, f)

    return {"balance": round_balance}

@app.route("/portfolio")
def portfolio():
    with open("user.json", "r") as f:
        user_data = json.load(f)

    address = user_data.get("address", "")
    cached_balance = user_data.get("last_balance", 0.0)
    
    return render_template("portfolio.html", balance=round(cached_balance, 2))

@app.route('/accounts')
def accounts():
    with open("user.json", "r") as f:
        user_data = json.load(f)
    
    address = user_data.get("address", "")
    balance = round_down_4(get_balance_cached(address))
    return render_template('accounts.html', balance=balance-1)

@app.route("/receive")
def receive():
    generate_xrp_qr()
    with open("user.json", "r") as f:
        address = json.load(f)["address"]
    return render_template("receive.html", address=address, salt=os.urandom(16).hex())

@app.route('/reset_account', methods=['POST'])
def reset_account():
    try:
        os.remove('user.json')
    except FileNotFoundError:
        pass
    return redirect(url_for('index'))

@app.route("/build")
def build():
    with open("user.json", "r") as f:
        user_data = json.load(f)
    
    output_path = user_data["output_path"]
    address = user_data["address"]
    
    balance = get_balance_cached(address)
    max_amount = round(balance - 1.00002,4)
    return render_template("build.html", output_path=output_path, max_amount=max_amount)

@app.route("/build_transaction", methods=["POST"])
def save_tx():
    recipient = request.form.get("address")
    amount = request.form.get("amount")
    dt = request.form.get("dt", "")

    path = save_unsigned_transaction(recipient, amount, dt) 

    return redirect("/build")

@app.route("/change_output_path", methods=["POST"])
def change_output_path():
    new_path = request.form.get("new_output_path", "")
    
    if not new_path:
        return redirect("/build")
    
    if not os.path.isdir(new_path):
        return render_template("build.html", output_path="INVALID ADDRESS")
    
    with open("user.json", "r") as f:
        user_data = json.load(f)
    user_data["output_path"] = new_path
    with open("user.json", "w") as f:
        json.dump(user_data, f)
    
    return redirect("/build")


@app.route("/support")
def support():
    return render_template("support.html")

@app.route("/send", methods=["GET", "POST"])
def send():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            return render_template("send.html", error="No file uploaded.")

        try:
            tx_data = json.load(file)
        except json.JSONDecodeError:
            return render_template("send.html", error="Invalid JSON file.")

        try:
            result = send_signed_tx_from_data(tx_data)
            if result["engine_result"] == "tesSUCCESS":
                tx_hash = result["tx_json"]["hash"]
                tx_url = f"https://xrpscan.com/tx/{tx_hash}"
                return render_template("send.html", success=True, tx_url=tx_url)
            else:
                if result["engine_result"] == "tefPAST_SEQ":
                    error = "Transaction already sent. (Or other problem)"
                return render_template("send.html", success=False, error=error)
        except:
            return render_template("send.html", success=False)

    return render_template("send.html")