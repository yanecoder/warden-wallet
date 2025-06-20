import json
import sys
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment
from xrpl.transaction import submit

client = JsonRpcClient("https://s1.ripple.com:51234")

def send_signed_tx_from_data(signed_tx_data: dict):
    signed_tx = Payment.from_xrpl(signed_tx_data)
    response = submit(signed_tx, client)
    return response.result
