import os
import json
from flask import render_template, redirect, request
from app import app

from wallet.create import generate_mnemonic, get_address, is_valid_mnemonic, mnemonic_to_private_key
from wallet.sign import sign_transaction_from_data

DATA_FILE = "private.json"


def save_mnemonic(mnemo: str) -> None:
    private_key = mnemonic_to_private_key(mnemo)
    default_output = os.path.expanduser("~") 

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                prev = json.load(f)
                default_output = prev.get("output_path", default_output)
        except Exception:
            pass                                       

    data = {
        "mnemonic": mnemo,
        "private_key": private_key,
        "output_path": default_output
    }

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_user_data():
    if not os.path.exists(DATA_FILE):
        return None
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/create')
def create_wallet():
    mnemo = generate_mnemonic()
    address = get_address(mnemo)
    save_mnemonic(mnemo)
    return render_template("create.html", mnemonic=mnemo, address=address)


@app.route('/enter', methods=['GET', 'POST'])
def enter():
    if request.method == 'POST':
        mnemo = request.form['mnemonic'].strip()
        if is_valid_mnemonic(mnemo):
            save_mnemonic(mnemo)
            return redirect('/')
        return render_template("enter.html", error="Invalid seed phrase")
    return render_template("enter.html")


@app.route('/reset')
def reset_wallet():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    return redirect('/')


@app.route("/sign", methods=["GET", "POST"])
def sign():
    user_data = load_user_data()
    if not user_data:
        return render_template("sign.html", no_wallet=True)

    output_path = user_data.get("output_path", os.path.expanduser("~"))

    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            return render_template("sign.html", output_path=output_path, error="No file uploaded")

        try:
            tx_data = json.load(file)
            signed_tx = sign_transaction_from_data(tx_data)

            output_file = os.path.join(output_path, "stx.json")
            with open(output_file, "w") as f:
                json.dump(signed_tx, f, indent=2)

            return render_template("sign.html", success=True, path=output_file, output_path=output_path)

        except Exception as e:
            return render_template("sign.html", output_path=output_path, error=str(e))

    return render_template("sign.html", output_path=output_path)


@app.route("/change_output_path", methods=["POST"])
def change_output_path():
    new_path = request.form.get("new_output_path", "").strip()
    if not new_path or not os.path.isdir(new_path):
        return redirect("/sign")

    user_data = load_user_data()
    if user_data:
        user_data["output_path"] = new_path
        with open(DATA_FILE, "w") as f:
            json.dump(user_data, f)
    return redirect("/sign")
