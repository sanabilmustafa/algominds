import base64
import hashlib
import hmac
import json
import requests
import os
import CREDENTIALS
import pprint
from pathlib import Path
import datetime

userid = CREDENTIALS.userid         
password = CREDENTIALS.password         
secret_key = CREDENTIALS.secret_key    
key = secret_key.encode()

CREDENTIALS_FILE = os.path.abspath('CREDENTIALS.py')

inner_data = "{" + f'"username":"{userid}","password":"{password}"' + "}"

encoded_json = base64.b64encode(inner_data.encode()).decode()


message = encoded_json.encode()
hmac_sha256 = hmac.new(key, message, hashlib.sha256)
sha_result = hmac_sha256.hexdigest()


final_auth_string = f"{encoded_json}.{sha_result}"
url = f"{CREDENTIALS.tradingAPI}/pu/user-auth/client-auth"
payload = {"body": final_auth_string}


headers = {
    "Content-Type": "application/json",
    "Accept": "*/*"
}
payload = {
    "body": final_auth_string
}

response = requests.post(url, json=payload, headers=headers)
auth_response = response.json()
print("Auth Response:", auth_response)

socket_token = auth_response["socket_token"]
auth_headers = response.headers
auth_token = auth_headers['Authorization']
refresh_token = auth_headers['X-Refresh-Token']
auth_headers = {
    "Authorization": f"{auth_token}",
    "X-Refresh-Token": refresh_token
}

print("Headers used in client auth:", auth_headers)

market_status_url = f"{CREDENTIALS.tradingAPI}/pr/market/status"

market_status_response = requests.get(market_status_url, headers=auth_headers)
print("Raw Response:", market_status_response.text)
print("Market Status Response:", market_status_response.json())

client_code_url = f"{CREDENTIALS.tradingAPI}/pr/client/codes"
client_code_response = requests.get(client_code_url, headers=auth_headers)
print("raw data: ", client_code_response.text)
print("client code json: ", client_code_response.json())

def get_activity_logs():
    activity_log_url = f"{CREDENTIALS.tradingAPI}/pr/other/activity-logs?headers=1&hTerminalNo=&account=&hOrdSides=BUY&mktType=&symbol=KEL"
    activity_log_response = requests.get(activity_log_url, headers=auth_headers)
    print("activity logs json: ", activity_log_response.json())
    return activity_log_response.json()

def get_outstanding_logs():
    outstanding_logs_url = f"{CREDENTIALS.tradingAPI}/pr/trade/outstanding-orders?hTerminalNo=&mktType=&account=&symbol=&hOrderId=&orderId=&hOrdSides=BUY"
    outstanding_logs_response = requests.get(outstanding_logs_url, headers=auth_headers)
    print("outstanding logs json: ", outstanding_logs_response.json())

    return outstanding_logs_response.json()
    # return "hello"


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
    print(f"updated the {key}")

client_exposure_url = f"{CREDENTIALS.tradingAPI}/pr/client/exposure?mode=S&account={CREDENTIALS.client_code}"
client_exposure_response = requests.get(client_exposure_url, headers=auth_headers).json()
print("raw data of client exposure: ", client_exposure_response)

update_credential("socket_token", f"{socket_token}")
update_credential("Authorization", f"{auth_token}")
update_credential("X_Refresh_Token", f"{refresh_token}")
update_credential("client_code", 222)

update_credential("pendingOrderValue", float(client_exposure_response['data']['pendingOrderValue']))
update_credential("portfolioMarketValue", float(client_exposure_response['data']['portfolioMarketValue']))
update_credential("totalWorth", float(client_exposure_response['data']['TotalWorth']))
update_credential("balance", float(client_exposure_response['data']['Balance']))
update_credential("cashWithdrawalLimit", float( client_exposure_response['data']['CashWithdrawalLimit']))

import json, csv

# Save as JSON
with open("portfolio.json", "w") as f:
    json.dump(client_exposure_response['data']['portfolioDetails'], f, indent=2)

# Save as CSV
with open("portfolio.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerows(client_exposure_response['data']['portfolioDetails'])


with open("portfolio.json") as f:
    portfolio = json.load(f)
    
auth_response = auth_response  # already in your script
market_status = market_status_response.json()
client_codes = client_code_response.json()
activity_logs = get_activity_logs()
outstanding_orders = get_outstanding_logs()
client_exposure = client_exposure_response

# Report template
html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Trading API Report</title>
    <style>
        body {{
            font-family: 'Poppins', sans-serif;
            margin: 2rem;
            background-color: #f9f9f9;
            color: #333;
        }}
        h1 {{
            color: #007BFF;
        }}
        h2 {{
            border-bottom: 2px solid #007BFF;
            padding-bottom: 0.3rem;
        }}
        .section {{
            margin-bottom: 2rem;
        }}
        .json-block {{
            background: #f0f0f0;
            padding: 1rem;
            border-radius: 8px;
            font-family: monospace;
            white-space: pre-wrap;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}
        table, th, td {{
            border: 1px solid #ccc;
        }}
        th, td {{
            padding: 0.5rem;
            text-align: center;
        }}
        th {{
            background-color: #007BFF;
            color: white;
        }}
        .timestamp {{
            font-size: 0.9rem;
            color: #777;
            margin-top: -1rem;
        }}
    </style>
</head>
<body>
    <h1>Trading API Report</h1>
    <p class="timestamp">Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <div class="section">
        <h2>🛡️ Auth Response</h2>
        <div class="json-block">{json.dumps(auth_response, indent=2)}</div>
    </div>

    <div class="section">
        <h2>📈 Market Status</h2>
        <div class="json-block">{json.dumps(market_status, indent=2)}</div>
    </div>

    <div class="section">
        <h2>👤 Client Codes</h2>
        <div class="json-block">{json.dumps(client_codes, indent=2)}</div>
    </div>

    <div class="section">
        <h2>📜 Activity Logs (KEL)</h2>
        <div class="json-block">{json.dumps(activity_logs, indent=2)}</div>
    </div>

    <div class="section">
        <h2>📊 Outstanding Orders</h2>
        <div class="json-block">{json.dumps(outstanding_orders, indent=2)}</div>
    </div>

    <div class="section">
        <h2>💼 Client Exposure Summary</h2>
        <div class="json-block">{json.dumps(client_exposure['data'], indent=2)}</div>
    </div>

    <div class="section">
        <h2>📋 Portfolio Table</h2>
        <table>
            <thead>
                <tr>
                    {"".join(f"<th>Col {i+1}</th>" for i in range(len(portfolio[0])))}
                </tr>
            </thead>
            <tbody>
                {''.join('<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>' for row in portfolio)}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

# Save the HTML report
report_path = Path("report.html")
report_path.write_text(html, encoding="utf-8")
print(f"✅ Report generated at: {report_path.resolve()}")