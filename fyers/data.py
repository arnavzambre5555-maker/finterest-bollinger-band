from datetime import datetime
import pandas as pd

class FyersData:
    def __init__(self, fyers_instance):
        self.fyers = fyers_instance
    
    def get_historical_data(self, symbol, from_date, to_date, resolution='D'):
        from_ts = int(datetime.strptime(from_date, '%Y-%m-%d').timestamp())
        to_ts = int(datetime.strptime(to_date, '%Y-%m-%d').timestamp())
        
        data_params = {
            'symbol': symbol,
            'resolution': resolution,
            'date_format': '1',
            'range_from': str(from_ts),
            'range_to': str(to_ts),
            'cont_flag': '1'
        }
        
        response = self.fyers.history(data=data_params)
        
        if response.get('code') == 200:
            candles = response['candles']
            df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['date'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('date', inplace=True)
            df = df[['open', 'high', 'low', 'close', 'volume']]
            return df
        return None
