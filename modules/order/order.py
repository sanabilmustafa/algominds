# #from wsorder.py
# import ssl
# import websocket
# import threading
# import json
# import hashlib
# import string
# import random
# import CREDENTIALS
# from .utils import log_order
# import time
# from . import order_bp
# from flask import Flask, render_template, request, redirect, flash, jsonify

# from .api_calls import get_outstanding_orders, get_activity_logs , get_client_auth

# ws = None  
# stop_event = threading.Event()
# orderHash = ""
# keyof11 = ""
# keyof37 = ""

# sent_orders = {}
# @order_bp.route('/', methods=['GET', 'POST'])
# def order_home():
#     try:
#         print("inside Order route")

#         if request.method == 'POST':
#             try:
#                 print("Form submitted!")
#                 user_id = request.form['user_id']
#                 pin = int(request.form['pin'])
#                 qty = int(request.form['qty'])
#                 disc = int(request.form['disc'])
#                 order_type = int(request.form['order_type'])
#                 price = float(request.form['price'])
#                 symbol = request.form['symbol']
#                 side = request.form['side']
#                 client_code = request.form['client_code']
#                 display_qty = request.form['display_qty']
#                 market_code = request.form['market_code']

#                 limit_price = request.form.get('lmtprice')  # optional, only for SLO

#                 print(user_id, pin, qty, price, symbol, side, order_type, 
#                       client_code, display_qty, market_code)
                
#                 if order_type == 3:
#                     payload = createSLOOrderPayload(
#                         user_id, pin, qty, price, symbol, side, limit_price,
#                         client_code, display_qty, market_code
#                     )
#                 else:
#                     payload = createOrderPayload(
#                         user_id, pin, qty, price, symbol, side, order_type,
#                         client_code, display_qty, market_code
#                     )

#                 print("Payload:", payload)
#                 print("Order has been sent!", "success")
#             except Exception as e:
#                 print(f"Error: {str(e)}", "danger")

#             return redirect('/')

#         elif request.method == 'GET':
#             print("Authenticating before fetching orders...")

#             # auth_headers, token, resp = get_client_auth(CREDENTIALS.userid, CREDENTIALS.password)
#             # print("Auth result:", auth_headers, token, resp)

#             outstanding_logs = get_outstanding_orders()
#             activity_logs = get_activity_logs()

#             return render_template('order.html',
#                                    outstanding_logs=[],
#                                    activity_logs=[])

#     except Exception as e:
#         return f"❌ Template Error: {str(e)}", 500

# def checkORderConditions(qty, price):
#     if CREDENTIALS.balance <= 0 and (qty * price) > CREDENTIALS.balance and (qty * price) > CREDENTIALS.cashWithdrawalLimit:
#         return False
#     else: 
#         return True
# def generateOrderHash():
#     rand_str = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
#     return hashlib.md5(rand_str.encode()).hexdigest()

# # Prepare order payload
# def createOrderPayload(user_id, pin, qty, price, symbol, side, order_type, client_code, display_qty, market_code):
#     return [
#         7,
#         "newOrder",
#         {
#             "userId": user_id,
#             "pin": pin,
#             "ordHash": generateOrderHash(),
#             "38": qty,
#             "40": order_type,
#             "44": price,
#             "54": side,
#             "55": symbol, 
#             "59": "0",
#             "99": 0.0,
#             "448": client_code,
#             "1138": str(display_qty),
#             "1180": market_code
#         }
#     ]
#     print("SIMPLE MKT-LMT ORDER IS SENT")

# # Prepare order payload
# def createSLOOrderPayload(user_id, pin, qty, price, symbol, side, limit_price, client_code, display_qty, market_code):
#     return [
#         7,
#         "newSlo",
#         {
#             "userId": user_id,
#             "pin": pin,
#             "ordHash": generateOrderHash(),
#             "38": qty,
#             "40": 2,
#             "44": price,
#             "54": side,
#             "55": symbol,
#             "59": "0",
#             "99": limit_price, #this is what is different in the slo order. it must contain a value rather than being 0.0
#             "448": client_code,
#             "1138": str(display_qty),
#             "1180": market_code
#         }
#     ]
#     print("SLO-ORDER IS SENT")

# # WebSocket callbacks
# def on_message(ws, message):
#     print("Received from ws:", message)
#     try:
#         data = json.loads(message)
#         if data.get("t") == "or":
#             order_response = data["d"]
#             # Optional: print or log
#             print(f"✅ Order Response: {order_response}")
#             global orderHash, keyof11, keyof37
#             orderHash = order_response["ordHash"]
#             keyof11 = order_response["11"]
#             keyof37 = order_response["37"]
#             print("order hash: ", orderHash, "11: ", keyof11, "37: ", keyof37)

#             # Extract last sent order details for logging
#             if "ordHash" in order_response:
#                 # You'll need to keep a mapping of order hashes to symbol/side/price
#                 if order_response["ordHash"] in sent_orders:
#                     order_meta = sent_orders[order_response["ordHash"]]
#                     log_order(
#                         symbol=order_meta["symbol"],
#                         side=order_meta["side"],
#                         price=order_meta["price"],
#                         response=order_response
#                     )
     
#     except Exception as e:
#         print(f"⚠️ Error parsing order message: {e}")

# def on_open(ws):
#     print("✅ WebSocket connected.")

# def on_error(ws, error):
#     print("❌ WebSocket error:", error)

# def on_close(ws, code, reason):
#     print(f"🔒 WebSocket closed: {code}, {reason}") 
# # Open WebSocket once
# def start_socket():
#     global ws
#     ws_url = f"{CREDENTIALS.wsAPI}?socket_token={CREDENTIALS.socket_token}"
#     ws = websocket.WebSocketApp(
#         ws_url,
#         subprotocols=["wamp"],
#         on_open=on_open,
#         on_message=on_message,
#         on_error=on_error,
#         on_close=on_close,
#     )
#     # thread = threading.Thread(target=ws.run_forever)
#     thread = threading.Thread(
#     target=ws.run_forever,
#     kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}}
# )
#     thread.daemon = True
#     thread.start()

# # Send an order any time
# def send_SLO_order(user_id, pin, qty, price, symbol, side, limit_price, client_code, display_qty, market_code):
#     print("inside send order ---------------")
#     global ws
#     if ws:
#         order = createSLOOrderPayload(user_id, pin, qty, price, symbol, side, limit_price, client_code, display_qty, market_code)
#         ord_hash = order[2]["ordHash"]
        
#         sent_orders[ord_hash] = {
#             "symbol": symbol,
#             "side": "buy" if side == 1 else "sell",
#             "price": price
#         }
#         print("send order ---> ", order)
#         # ws.send(json.dumps(order))
#     else:
#         print("⚠️ WebSocket is not connected.")
        
# # Send an order any time
# def send_order(user_id, pin, qty, price, symbol, side, order_type, client_code, display_qty, market_code):
#     print("inside send order ---------------")
#     global ws
#     if ws:
#         order = createOrderPayload(user_id, pin, qty, price, symbol, side, order_type, client_code, display_qty, market_code)
#         ord_hash = order[2]["ordHash"]
        
#         sent_orders[ord_hash] = {
#             "symbol": symbol,
#             "side": "buy" if side == 1 else "sell", 
#             "price": price
#         }
#         # print("send order ---> ", order)
#         ws.send(json.dumps(order))
#     else:
#         print("⚠️ WebSocket is not connected.")


# connection_ready = threading.Event()

# def cancel_order(ordhash, keyof11, keyof37):
#     global ws
#     if ws:
#         cancel_order = [
#         7, 
#         "cancelOrder", 
#             { 
#                 "userId": "TEST05", 
#                 "pin": "1111", 
#                 "ordHash": str(ordhash), 
#                 "37": str(keyof37), 
#                 "41": str(keyof11), 
#                 "54": "1", 
#                 "55": "WTL", 
#                 "448": "222", 
#                 "1180": "01" 
#             } 
#         ]
#         print(cancel_order)
#         return ws.send(json.dumps(cancel_order));
#     print("order cancelled")



# start_socket()

# # def delayed_cancel():
# #     print("about to cancel order")
# #     cancel_order(orderHash, keyof11, keyof37)

# # print("⏳ Will cancel order in 15 seconds...")
# # threading.Timer(10.0, delayed_cancel).start()
# # try:
# #     while True:
# #         pass
# # except KeyboardInterrupt:
# #     print("Interrupted")










#from wsorder.py
import ssl
import websocket
import threading
import json
import hashlib
import string
import random
import CREDENTIALS
from .utils import log_order
import time
from . import order_bp
from flask import Flask, render_template, request, redirect, flash, jsonify

from .api_calls import get_outstanding_orders, get_activity_logs , get_client_auth

ws = None  
stop_event = threading.Event()
orderHash = ""
keyof11 = ""
keyof37 = ""

sent_orders = {}
@order_bp.route('/', methods=['GET', 'POST'])
def order_home():
    try:
        print("inside Order route")

        if request.method == 'POST':
            try:
                print("Form submitted!")
                user_id = request.form['user_id']
                pin = int(request.form['pin'])
                qty = int(request.form['qty'])
                disc = int(request.form['disc'])
                order_type = int(request.form['order_type'])
                price = float(request.form['price'])
                symbol = request.form['symbol']
                side = request.form['side']
                client_code = request.form['client_code']
                display_qty = request.form['display_qty']
                market_code = request.form['market_code']

                limit_price = request.form.get('lmtprice')  # optional, only for SLO

                print(user_id, pin, qty, price, symbol, side, order_type, 
                      client_code, display_qty, market_code)
                
                if order_type == 3:
                    payload = createSLOOrderPayload(
                        user_id, pin, qty, price, symbol, side, limit_price,
                        client_code, display_qty, market_code
                    )
                else:
                    payload = createOrderPayload(
                        user_id, pin, qty, price, symbol, side, order_type,
                        client_code, display_qty, market_code
                    )

                print("Payload:", payload)
                print("Order has been sent!", "success")
            except Exception as e:
                print(f"Error: {str(e)}", "danger")

            return redirect('/')

        elif request.method == 'GET':
            print("Authenticating before fetching orders...")

            # auth_headers, token, resp = get_client_auth(CREDENTIALS.userid, CREDENTIALS.password)
            # print("Auth result:", auth_headers, token, resp)

            # outstanding_logs = get_outstanding_orders()
            # activity_logs = get_activity_logs()

            return render_template('order.html',
                                   outstanding_logs=[],
                                   activity_logs=[])

    except Exception as e:
        return f"❌ Template Error: {str(e)}", 500

def checkORderConditions(qty, price):
    if CREDENTIALS.balance <= 0 and (qty * price) > CREDENTIALS.balance and (qty * price) > CREDENTIALS.cashWithdrawalLimit:
        return False
    else: 
        return True
def generateOrderHash():
    rand_str = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return hashlib.md5(rand_str.encode()).hexdigest()

# Prepare order payload
def createOrderPayload(user_id, pin, qty, price, symbol, side, order_type, client_code, display_qty, market_code):
    return [
        7,
        "newOrder",
        {
            "userId": user_id,
            "pin": pin,
            "ordHash": generateOrderHash(),
            "38": qty,
            "40": order_type,
            "44": price,
            "54": side,
            "55": symbol, 
            "59": "0",
            "99": 0.0,
            "448": client_code,
            "1138": str(display_qty),
            "1180": market_code
        }
    ]
    print("SIMPLE MKT-LMT ORDER IS SENT")

# Prepare order payload
def createSLOOrderPayload(user_id, pin, qty, price, symbol, side, limit_price, client_code, display_qty, market_code):
    return [
        7,
        "newSlo",
        {
            "userId": user_id,
            "pin": pin,
            "ordHash": generateOrderHash(),
            "38": qty,
            "40": 2,
            "44": price,
            "54": side,
            "55": symbol,
            "59": "0",
            "99": limit_price, #this is what is different in the slo order. it must contain a value rather than being 0.0
            "448": client_code,
            "1138": str(display_qty),
            "1180": market_code
        }
    ]
    print("SLO-ORDER IS SENT")

# WebSocket callbacks
def on_message(ws, message):
    print("Received:", message)
    try:
        data = json.loads(message)
        if data.get("t") == "or":
            order_response = data["d"]
            # Optional: print or log
            print(f"✅ Order Response: {order_response}")
            global orderHash, keyof11, keyof37
            orderHash = order_response["ordHash"]
            keyof11 = order_response["11"]
            keyof37 = order_response["37"]
            print("order hash: ", orderHash, "11: ", keyof11, "37: ", keyof37)

            # Extract last sent order details for logging
            if "ordHash" in order_response:
                # You'll need to keep a mapping of order hashes to symbol/side/price
                if order_response["ordHash"] in sent_orders:
                    order_meta = sent_orders[order_response["ordHash"]]
                    log_order(
                        symbol=order_meta["symbol"],
                        side=order_meta["side"],
                        price=order_meta["price"],
                        response=order_response
                    )
     
    except Exception as e:
        print(f"⚠️ Error parsing order message: {e}")

def on_open(ws):
    print("✅ WebSocket connected.")

def on_error(ws, error):
    print("❌ WebSocket error:", error)

def on_close(ws, code, reason):
    print(f"🔒 WebSocket closed: {code}, {reason}") 
# Open WebSocket once
def start_socket():
    global ws
    ws_url = f"{CREDENTIALS.wsAPI}?socket_token={CREDENTIALS.socket_token}"
    ws = websocket.WebSocketApp(
        ws_url,
        subprotocols=["wamp"],
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    # thread = threading.Thread(target=ws.run_forever)
    thread = threading.Thread(
    target=ws.run_forever,
    kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}}
)
    thread.daemon = True
    thread.start()

# Send an order any time
def send_SLO_order(user_id, pin, qty, price, symbol, side, limit_price, client_code, display_qty, market_code):
    print("inside send order ---------------")
    global ws
    if ws:
        order = createSLOOrderPayload(user_id, pin, qty, price, symbol, side, limit_price, client_code, display_qty, market_code)
        ord_hash = order[2]["ordHash"]
        
        sent_orders[ord_hash] = {
            "symbol": symbol,
            "side": "buy" if side == 1 else "sell",
            "price": price
        }
        print("send order ---> ", order)
        # ws.send(json.dumps(order))
    else:
        print("⚠️ WebSocket is not connected.")
        
# Send an order any time
def send_order(user_id, pin, qty, price, symbol, side, order_type, client_code, display_qty, market_code):
    print("inside send order ---------------")
    global ws
    if ws:
        order = createOrderPayload(user_id, pin, qty, price, symbol, side, order_type, client_code, display_qty, market_code)
        ord_hash = order[2]["ordHash"]
        
        sent_orders[ord_hash] = {
            "symbol": symbol,
            "side": "buy" if side == 1 else "sell", 
            "price": price
        }
        # print("send order ---> ", order)
        ws.send(json.dumps(order))
    else:
        print("⚠️ WebSocket is not connected.")


connection_ready = threading.Event()

def cancel_order(ordhash, keyof11, keyof37):
    global ws
    if ws:
        cancel_order = [
        7, 
        "cancelOrder", 
            { 
                "userId": "TEST05", 
                "pin": "1111", 
                "ordHash": str(ordhash), 
                "37": str(keyof37), 
                "41": str(keyof11), 
                "54": "1", 
                "55": "WTL", 
                "448": "222", 
                "1180": "01" 
            } 
        ]
        print(cancel_order)
        return ws.send(json.dumps(cancel_order));
    print("order cancelled")



start_socket()

# def delayed_cancel():
#     print("about to cancel order")
#     cancel_order(orderHash, keyof11, keyof37)

# print("⏳ Will cancel order in 15 seconds...")
# threading.Timer(10.0, delayed_cancel).start()
# try:
#     while True:
#         pass
# except KeyboardInterrupt:
#     print("Interrupted")
