import re

def is_valid_xrp_address(address: str) -> bool:
    return bool(re.fullmatch(r"^r[1-9A-HJ-NP-Za-km-z]{24,34}$", address))