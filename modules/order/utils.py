from datetime import datetime

def log_order(symbol, side, price, response):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "success" if response.get("success") else "FAILED"
    ord_hash = response.get("ordHash", "N/A")
    order_ref = response.get("11", "N/A")

    log_entry = (
        f"[{now}] {side.upper()} Order Placed for {symbol} at price {price}\n"
        f"Order Hash: {ord_hash}\n"
        f"Order Ref No (11): {order_ref}\n"
        f"Server Response: {status}\n\n"
    )

    with open("trade_report.txt", "a") as f:
        f.write(log_entry)
