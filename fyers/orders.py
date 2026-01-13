class FyersOrders:
    def __init__(self, fyers_instance):
        self.fyers = fyers_instance
    
    def place_market_order(self, symbol, qty, side):
        order_data = {
            'symbol': symbol,
            'qty': qty,
            'type': 2,
            'side': side,
            'productType': 'CNC',
            'limitPrice': 0,
            'stopPrice': 0,
            'validity': 'DAY',
            'disclosedQty': 0,
            'offlineOrder': False
        }
        
        response = self.fyers.place_order(data=order_data)
        return response
    
    def buy(self, symbol, qty):
        return self.place_market_order(symbol, qty, 1)
    
    def sell(self, symbol, qty):
        return self.place_market_order(symbol, qty, -1)
