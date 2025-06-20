import requests

def get_xrp_price(xrp_amount):
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {'symbol': 'XRPUSDT'}
    
    response = requests.get(url, params=params)
    data = response.json()
    
    xrp_price = float(data['price'])
    total_price = xrp_price * xrp_amount
    return total_price