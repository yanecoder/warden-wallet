import json
import os
from xrpl.models.transactions import Payment

def save_unsigned_transaction(recipient, amount_str, destination_tag=None):
    amount_xrp = amount_str.replace(",", ".")
    drops = str(int(float(amount_xrp) * 1_000_000))

    with open("user.json", "r") as f:
        user_data = json.load(f)

    sender_address = user_data["address"]

    tx_kwargs = {
        "account": sender_address,
        "destination": recipient,
        "amount": drops,
        "fee": "10",
    }

    if destination_tag and destination_tag.isdigit():
        tx_kwargs["destination_tag"] = int(destination_tag)

    tx = Payment(**tx_kwargs)

    output_path = user_data["output_path"]
    path = os.path.join(output_path, "utx.json")

    with open(path, "w") as f:
        f.write(json.dumps(tx.to_xrpl(), indent=2))

    return path
