import qrcode
import json
import os

def generate_xrp_qr():
    with open("user.json", "r") as f:
        user_data = json.load(f)

    address = user_data["address"]
    uri = f"ripple:{address}"

    current_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(current_dir, "..", "static", "qr")
    os.makedirs(static_dir, exist_ok=True)

    qr_path = os.path.join(static_dir, "qr_code.png")
    img = qrcode.make(uri)
    img.save(qr_path)
