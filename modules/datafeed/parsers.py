import datetime
import pytz

def parse_numeric(value):
    if value == '':
        return None
    try:
        return float(value) if '.' in value else int(value)
    except ValueError:
        return None

# -------------------------
# Market by Order (MBO)
# -------------------------
def parse_mbo(mbo_string):
    # Remove the trailing |*
    mbo_string = mbo_string.strip()
    if mbo_string.endswith("|*"):
        mbo_string = mbo_string[:-2]

    # Ensure it starts with MBO|
    if not mbo_string.startswith("MBO|"):
        raise ValueError("Invalid MBO format: does not start with 'MBO|'")
    
    # Remove the "MBO|" prefix
    mbo_string = mbo_string[4:]

    # Split into main parts
    parts = mbo_string.split(";")
    if len(parts) < 6:
        raise ValueError("Invalid MBO format: missing parts")

    symbol = parts[0]
    instrument = parts[1]

    # Find BUY/SELL sections
    try:
        buy_index = parts.index("BUY")
        sell_index = parts.index("SELL")
    except ValueError:
        raise ValueError("Invalid MBO format: missing BUY or SELL sections")

    buy_orders_raw = parts[buy_index + 1 : sell_index]
    sell_orders_raw = parts[sell_index + 1 :]

    # The last sell part might have an empty string at the end
    sell_orders_raw = [o for o in sell_orders_raw if o]

    def parse_orders(order_parts):
        orders = []
        for part in order_parts:
            if not part.strip():
                continue
            for order_str in part.split("$"):
                if not order_str.strip():
                    continue
                fields = order_str.split(",")
                if len(fields) != 4:
                    continue
                price, qty, side_code, order_id = fields
                orders.append({
                    "price": float(price),
                    "quantity": float(qty),
                    "side_code": side_code,
                    "order_id": order_id
                })
        return orders

    return {
        "symbol": symbol,
        "market_code": instrument,
        "buy_orders": parse_orders(buy_orders_raw),
        "sell_orders": parse_orders(sell_orders_raw)
    }

# -------------------------
# Market by Price (MBP)
# -------------------------
def parse_mbp(raw_data):
    parts = raw_data.strip("|*").split(";")
    header = parts[0].split("|")  # ['MBP', 'BWCL']
    record_identifier = header[0]
    symbol_code = header[1]
    market_code = parts[1] if len(parts) > 1 else None

    buy_levels = []
    sell_levels = []
    current_side = None

    for segment in parts[2:]:
        segment = segment.strip()
        if not segment:
            continue
        
        if segment.startswith("BUY"):
            current_side = "buy"
            segment = segment[4:]  # Remove 'BUY;'
        elif segment.startswith("SELL"):
            current_side = "sell"
            segment = segment[5:]  # Remove 'SELL;'

        if "$" in segment:
            for level_str in segment.strip(";").split("$"):
                if not level_str:
                    continue
                fields = level_str.split(",")
                if len(fields) == 3:
                    order_count = parse_numeric(fields[0])
                    volume = parse_numeric(fields[1])
                    price = parse_numeric(fields[2])
                    level = {
                        "order_count": order_count,
                        "volume": volume,
                        "price": price
                    }
                    if current_side == "buy":
                        buy_levels.append(level)
                    elif current_side == "sell":
                        sell_levels.append(level)

    pkt_tz = pytz.timezone('Asia/Karachi')
    return {
        "record_identifier": record_identifier,
        "symbol_code": symbol_code,
        "market_code": market_code,
        "buy_levels": buy_levels,
        "sell_levels": sell_levels,
        "timestamp": datetime.datetime.now(pkt_tz)
    }
    
    
mbo_data = """ MBO|NBP;REG;BUY;139.210000,4500.00,dc,0010T0N8OI0131HB$139.210000,1000.00,dc,0010T0N8OI0131HM$139.200000,4798.00,dc,0010T0N8OI012ZFL$139.200000,10000.00,dc,0010T0N8OI01302A$139.190000,222.00,dc,0010T0N8OI0131RL$139.150000,200.00,dc,0010T0N8OI012YZ0$139.150000,1000.00,dc,0010T0N8OI012ZU5$139.120000,5000.00,dc,0010T0N8OI012Y8G$139.120000,25.00,dc,0010T0N8OI012ZYZ$139.070000,1000.00,dc,0010T0N8OI0130GX$;SELL;139.500000,490.00,dc,0010T0N8OI01304V$139.500000,25000.00,dc,0010T0N8OI01313E$139.550000,5000.00,dc,0010T0N8OI0130A3$139.590000,10000.00,dc,0010T0N8OI012ZT5$139.600000,12945.00,dc,0010T0N8OI012YP0$139.790000,500.00,dc,0010T0N8OI012658$139.800000,475.00,dc,0010T0N8OI01235T$139.800000,25000.00,dc,0010T0N8OI012SKG$139.850000,10000.00,dc,0010T0N8OI012490$139.880000,10000.00,dc,0010T0N8OI011YRG$;|*"""

parsed = parse_mbo(mbo_data)
print(parsed)

mbp_data = """MBP|BWCL;REG;BUY;2,5.00,518.000000$1,10.00,517.100000$1,10.00,517.090000$1,10.00,517.080000$1,10.00,517.070000$1,10.00,517.050000$3,610.00,517.000000$1,8.00,516.500000$2,105.00,516.000000$2,110.00,515.500000$;SELL;2,75.00,519.000000$1,430.00,519.500000$1,1.00,519.600000$3,102.00,520.000000$1,1.00,520.200000$1,1.00,520.800000$1,1.00,521.000000$1,1.00,521.400000$1,200.00,521.990000$5,162.00,522.000000$;|*"""

print(parse_mbp(mbp_data))

