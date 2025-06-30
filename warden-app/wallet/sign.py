import json
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountInfo
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment
from xrpl.transaction import sign
from wallet.create import hex_priv_to_public_key

def sign_transaction_from_data(tx_data):
    with open("private.json", "r") as f:
        user_data = json.load(f)

    private_key = user_data["private_key"]
    public_key = hex_priv_to_public_key(private_key)
    wallet = Wallet(private_key=private_key, public_key=public_key)

    client = JsonRpcClient("https://s1.ripple.com:51234")

    account_info = AccountInfo(account=wallet.classic_address, ledger_index="current", strict=True)
    response = client.request(account_info)
    sequence = response.result["account_data"]["Sequence"]

    tx_data["Sequence"] = sequence
    tx_data["SigningPubKey"] = public_key

    unsigned_tx = Payment.from_xrpl(tx_data)

    signed_tx = sign(unsigned_tx, wallet)

    return signed_tx.to_xrpl()
