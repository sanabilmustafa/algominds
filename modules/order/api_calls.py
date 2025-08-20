
import json, csv
import base64
import hashlib
import hmac
import json
import requests
import os
from pathlib import Path
import datetime
import CREDENTIALS

CREDENTIALS_FILE = os.path.abspath('CREDENTIALS.py')

def update_credential(key, value):
    """Update or add a key-value pair in the credentials.py file."""
    with open(CREDENTIALS_FILE, 'r') as file:
        lines = file.readlines()

    found = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key} ="):
            lines[i] = f"{key} = {repr(value)}\n"
            found = True
            break

    if not found:
        lines.append(f"{key} = {repr(value)}\n")

    with open(CREDENTIALS_FILE, 'w') as file:
        file.writelines(lines)
    print(f"✅ Updated: {key}")

def get_client_auth(user, pw):
    """Authenticate and return auth headers + socket token"""
    # userid = CREDENTIALS.userid         
    # password = CREDENTIALS.password         
    print("inside get client auth")
    userid = user         
    password = pw      
    secret_key = CREDENTIALS.secret_key    
    key = secret_key.encode()

    inner_data = "{" + f'"username":"{userid}","password":"{password}"' + "}"
    encoded_json = base64.b64encode(inner_data.encode()).decode()
    message = encoded_json.encode()
    hmac_sha256 = hmac.new(key, message, hashlib.sha256)
    sha_result = hmac_sha256.hexdigest()
    final_auth_string = f"{encoded_json}.{sha_result}"

    url = f"{CREDENTIALS.tradingAPI}/pu/user-auth/client-auth"
    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*"
    }
    payload = {
        "body": final_auth_string
    }

    response = requests.post(url, json=payload, headers=headers, timeout=5)

    auth_response = response.json()
    if auth_response.get('success') == True:

        socket_token = auth_response["socket_token"]
        auth_headers = response.headers
        auth_token = auth_headers['Authorization']
        refresh_token = auth_headers['X-Refresh-Token']
        auth_headers = {
            "Authorization": f"{auth_token}",
            "X-Refresh-Token": refresh_token
        }

        
        update_credential("socket_token", f"{socket_token}")
        update_credential("Authorization", f"{auth_token}")
        update_credential("X_Refresh_Token", f"{refresh_token}")
        print("the function completd")
        return auth_headers, socket_token, auth_response
    else:
        print("❌ Authentication failed:", auth_response.get('message', 'Unknown error'))
        return None, None, auth_response

def get_market_status(headers):
    url = f"{CREDENTIALS.tradingAPI}/pr/market/status"
    return requests.get(url, headers=headers).json()


def get_client_codes(headers):
    url = f"{CREDENTIALS.tradingAPI}/pr/client/codes"
    return requests.get(url, headers=headers).json()


def get_activity_logs(headers, symbol="KEL"):
    url = f"{CREDENTIALS.tradingAPI}/pr/other/activity-logs?headers=1&hTerminalNo=&account=&hOrdSides=BUY&mktType=&symbol={symbol}"
    return requests.get(url, headers=headers).json()


def get_outstanding_orders():
    outstanding_logs_url = f"{CREDENTIALS.tradingAPI}/pr/trade/outstanding-orders?hTerminalNo=&mktType=&account=&symbol=&hOrderId=&orderId=&hOrdSides=BUY"
    headers, token, response = get_client_auth(CREDENTIALS.userid, CREDENTIALS.password)
    outstanding_logs_response = requests.get(outstanding_logs_url, headers=headers)
    print("outstanding logs json: ", outstanding_logs_response.json())

    return outstanding_logs_response.json()


def get_client_exposure(headers, client_code):
    url = f"{CREDENTIALS.tradingAPI}/pr/client/exposure?mode=S&account={client_code}"
    response = requests.get(url, headers=headers).json()

    # Update exposure fields in credentials
    exposure = response['data']
    update_credential("pendingOrderValue", float(exposure['pendingOrderValue']))
    update_credential("portfolioMarketValue", float(exposure['portfolioMarketValue']))
    update_credential("totalWorth", float(exposure['TotalWorth']))
    update_credential("balance", float(exposure['Balance']))
    update_credential("cashWithdrawalLimit", float(exposure['CashWithdrawalLimit']))

    # Save portfolio details
    with open("portfolio.json", "w") as f:
        json.dump(exposure['portfolioDetails'], f, indent=2)

    import csv
    with open("portfolio.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(exposure['portfolioDetails'])

    return response


# # Optional: main() if testing standalone
# if __name__ == "__main__":
#     headers, socket_token, auth_response = get_client_auth()
#     print("Auth Response:", auth_response)

#     market_status = get_market_status(headers)
#     print("Market Status:", market_status)

#     client_codes = get_client_codes(headers)
#     print("Client Codes:", client_codes)

#     activity_logs = get_activity_logs(headers, "KEL")
#     print("Activity Logs:", activity_logs)

#     outstanding_orders = get_outstanding_orders(headers)
#     print("Outstanding Orders:", outstanding_orders)

#     # You might need to update client_code before this
#     update_credential("client_code", 222)
#     exposure = get_client_exposure(headers, 222)
#     print("Client Exposure:", exposure)


