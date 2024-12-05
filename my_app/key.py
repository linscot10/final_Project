

import requests 
import json
from requests.auth import HTTPBasicAuth 
from datetime import datetime
import base64


class MpesaCredentials:
    consumer_key='p8vK4LqwlWR0VEG70Nq7OkiY0woQF3kRQcvZ1JAan5jYSAJI'
    consumer_secret='qnBGNAOaeVtowX5LRsxQreEW4YqM0gbbHJoU4QBGKWTDCjz1UNh0B6VYA5grl4Gv'
    api_url='https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    # https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials
    # api_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'

class MpesaAccessToken:
    r = requests.get(
        MpesaCredentials.api_url,
        auth=HTTPBasicAuth(MpesaCredentials.consumer_key, MpesaCredentials.consumer_secret)
    )

    
    print("API Response:", r.text)

    try:
        mpesa_access_token = json.loads(r.text)['access_token']
    except KeyError:
        print("Error: 'access_token' not found in the response.")
        print("Response:", r.text)
        raise Exception("Failed to retrieve M-Pesa access token")

    print("Access Token:", mpesa_access_token)

    

class MpesaPassword:
    lipa_time=datetime.now().strftime('%Y%m%d%H%M%S')
    bussiness_short_code='174379'
    offsetValue='0'
    passkey='bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    
    data_to_encode= bussiness_short_code+passkey+lipa_time
    online_password=base64.b64encode(data_to_encode.encode())
    decode_password=online_password.decode("utf-8")