import os
from fyers_apiv3 import fyersModel

class FyersAuth:
    def __init__(self):
        try:
            self.client_id = os.environ['FYERS_CLIENT_ID']
            self.secret_key = os.environ['FYERS_SECRET_KEY']
        except KeyError as e:
            raise ValueError(f"Missing required environment variable: {e}")
        
        self.redirect_uri = os.getenv('FYERS_REDIRECT_URI', 'https://www.google.com')
        self.access_token = None
    
    def generate_auth_url(self):
        session = fyersModel.SessionModel(
            client_id=self.client_id,
            secret_key=self.secret_key,
            redirect_uri=self.redirect_uri,
            response_type="code",
            grant_type="authorization_code"
        )
        return session.generate_authcode()
    
    def generate_token(self, auth_code):
        session = fyersModel.SessionModel(
            client_id=self.client_id,
            secret_key=self.secret_key,
            redirect_uri=self.redirect_uri,
            response_type="code",
            grant_type="authorization_code"
        )
        session.set_token(auth_code)
        response = session.generate_token()
        
        if response.get('code') == 200:
            self.access_token = response['access_token']
            return self.access_token
        return None
    
    def get_fyers_instance(self):
        if not self.access_token:
            token_file = 'fyers_access_token.txt'
            if os.path.exists(token_file):
                with open(token_file, 'r') as f:
                    self.access_token = f.read().strip()
        
        return fyersModel.FyersModel(
            client_id=self.client_id,
            token=self.access_token,
            log_path=""
        )
