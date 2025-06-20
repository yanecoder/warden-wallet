from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountInfo

client = JsonRpcClient("https://s1.ripple.com:51234")

def get_balance(address: str) -> str:
    if not address.startswith("r") or len(address) < 25:
        return 0.00
    try:
        req = AccountInfo(account=address, ledger_index="validated", strict=True)
        response = client.request(req)
        result = response.result

        if "account_data" in result:
            balance_drops = result["account_data"]["Balance"]
            return int(balance_drops) / 1_000_000
        else:
            return 0.00
    except Exception:
        return 0.00
