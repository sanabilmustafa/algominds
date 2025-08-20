# strategy_subscriber.py

import asyncio
import websockets
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from strategy_logic import tkt_modified_tsl_mod, sandbox, newTest
# Constants
DB_CONFIG = {
    'dbname': 'AlgoMinds',
    'user': 'algominds',
    'password': 'machinedatabase',
    'host': 'localhost',
    'port': 5432
    
}


WS_URI = 'ws://localhost:8765'


# Hardcoded indicators per strategy (this will later be dynamic or plugin-based)
STRATEGY_INDICATORS = {
    "TKT modified": ["SMA-200-D", "RSI-14-D", 'SMA-45-D'],
    "Long Term" : ["SMA-2-D", "SMA-5-D", "RSI-3-D"],
    # "TKT" : ["RSI-14-D"],
    
}

def get_active_deployed_strategies():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Fetch active and deployed strategies
    cur.execute("""
        SELECT strategy_id, strategy_name
        FROM strategies
        WHERE deploy_status = 'Deployed' AND status = 'Active'
    """)
    strategies = cur.fetchall()

    # Fetch symbols for each strategy
    strategy_subscriptions = []
    for strategy in strategies:
        cur.execute("""
            SELECT stock_symbol
            FROM strategy_stock_allocations
            WHERE strategy_id = %s
        """, (strategy['strategy_id'],))
        symbols = [row['stock_symbol'] for row in cur.fetchall()]

        indicators = STRATEGY_INDICATORS.get(strategy['strategy_name'], [])
        if symbols and indicators:
            strategy_subscriptions.append({
                'strategy_id': strategy['strategy_id'],
                'strategy_name': strategy['strategy_name'],
                'symbols': symbols,
                'indicators': indicators
            })

    cur.close()
    conn.close()
    print(strategy_subscriptions)
    return strategy_subscriptions

# def handle_incoming_data(data):
#     print("handle incoming data called")
#     symbol = data["symbol"]
#     tick = data["tick"]
#     indicators = data["indicators"]

#     # Decide which strategy to run based on strategy_name
#     # If you plan to run *all* strategies for the same symbol:
#     #   Loop through all in strategy_subscriptions
#     # For now, let's check dynamically:
#     strategy_name = data.get("strategy_name")

#     if strategy_name == "TKT modified":
#         tkt_modified_tsl_mod.run(symbol, tick, indicators, market_is_open=True)
#     elif strategy_name == "Long Term":
#         sandbox.run(symbol, tick, indicators, market_is_open=True)
strategy_subscriptions = []  

def handle_incoming_data(data):
    global strategy_subscriptions
    print("handle incoming data called")
    symbol = data["symbol"]
    tick = data["tick"]
    indicators = data["indicators"]

    # Loop through all strategies that include this symbol
    for strat in strategy_subscriptions:
        if symbol in strat['symbols']:
            if strat['strategy_name'] == "TKT modified":
                tkt_modified_tsl_mod.run(symbol, tick, indicators, market_is_open=True)
            elif strat['strategy_name'] == "Long Term":
                sandbox.run(symbol, tick, indicators, market_is_open=True)
            # elif strat['strategy_name'] == "TKT":
            #     newTest.run(symbol, tick, indicators, market_is_open=True)
                
                
# async def send_subscription(strategy_subs):
#     async with websockets.connect(WS_URI) as websocket:
#         print("✅ Connected to client-server")

#         for strategy in strategy_subs:
#             subscription = {
#                 "request": "subscribe",
#                 "symbols": strategy['symbols'],
#                 "indicators": strategy['indicators'],
#                 # "strategy_id": strategy['strategy_id']
#             }
#             print(f"📤 Sending subscription for {strategy['strategy_name']}:")
#             # print(json.dumps(subscription, indent=2))
#             print("sending subscription to client-server: ", json.dumps(subscription))
#             await websocket.send(json.dumps(subscription))

#         # Keep listening to incoming data (optional)
#         while True:
#             message = await websocket.recv()
#             data = json.loads(message)
#             print("📩 Received:", data)
#             handle_incoming_data(data)


async def send_subscription(strategy_subs):
    async with websockets.connect(WS_URI) as websocket:
        print("✅ Connected to client-server")

        # combine all symbols and indicators into a single subscribe
        all_symbols = set()
        all_indicators = set()
        for strategy in strategy_subs:
            all_symbols.update(strategy['symbols'])
            all_indicators.update(strategy['indicators'])

        subscription = {
            "request": "subscribe",
            "symbols": sorted(all_symbols),
            "indicators": sorted(all_indicators)
        }
        print("sending combined subscription to client-server:", json.dumps(subscription))
        await websocket.send(json.dumps(subscription))

        # keep listening for ticks
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print("📩 Received:", data)
            handle_incoming_data(data)
            
def main():
    global strategy_subscriptions
    strategy_subscriptions = get_active_deployed_strategies()
    print('Active deployed strategies:', strategy_subscriptions)
    if not strategy_subscriptions:
        print("❌ No active, deployed strategies found.")
        return

    asyncio.run(send_subscription(strategy_subscriptions))

if __name__ == "__main__":
    main()
    
# def run_strategies():
#     main()
