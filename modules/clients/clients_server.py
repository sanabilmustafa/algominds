import asyncio
import websockets
import json
import zmq
import zmq.asyncio
from collections import defaultdict
from datetime import datetime

from modules.indicators.calculator import sma, ema, rsi, macd, supertrend
from modules.indicators.state import get_historical_bars, update_symbol_history, get_last_trade
from modules.datafeed.utils import parse_feed  # Assumes your existing parse_feed function
# parse_feed: {"symbol_code": "OGDC", "open": ..., "high": ..., ...}
filename = "tick_cache.txt"
PORT = 8765
ZMQ_SERVER = "localhost"
ZMQ_PORT = 15012

clients = set()
subscriptions = {}  # websocket -> {"symbols": [...], "indicators": [...]}
tick_queue = asyncio.Queue()
live_tick_cache = {}  # symbol -> latest tick dict


async def handle_initial_subscription(websocket, symbols, indicators):
    for symbol in symbols:
        tick = live_tick_cache.get(symbol)
        if not tick:
            tick = await get_last_trade(symbol)

        if not tick:
            print(f"[WARN] No tick available for {symbol}")
            continue

        bars = await get_historical_bars(symbol)
        if not bars:
            print(f"[WARN] No historical bars for {symbol}")
            continue

        response = {
            "symbol": symbol,
            "tick": tick,
            "indicators": {}
        }

        for indicator_str in indicators:
            try:
                print("------------------------->",indicator_str)
                parts = indicator_str.split("-")
                name = parts[0].lower()  # 'RSI' -> 'rsi'
                length = int(parts[1]) if len(parts) > 1 else None
                timeframe = parts[2] if len(parts) > 2 else None
                
                bars = await get_historical_bars(symbol, timeframe)
                if not bars:
                    return
                
                if name == "sma":
                    # print(f"[DEBUG] Calculating SMA for {symbol} with length {length}")
                    result = sma(bars, length)[-1]
                elif name == "ema":
                    result = ema(bars, length)[-1]
                elif name == "rsi":
                    result = rsi(bars,length)[-1]
                elif name == "macd":
                    macd_line, _, _ = macd(bars)
                    result = macd_line[-1]
                elif name == "supertrend":
                    super_line, direction = supertrend(bars)
                    result = {"line": super_line[-1], "dir": direction[-1]}
                else:
                    result = None
                response["indicators"][indicator_str] = result
            except Exception as e:
                response["indicators"][indicator_str] = f"error: {str(e)}"

        try:
            await websocket.send(json.dumps(response, default=str))
        except Exception as e:
            print(f"[ERROR] Sending initial data to client: {e}")


async def register_client(websocket):
    try:
        async for message in websocket:
            data = json.loads(message)

            if data.get("request") == "subscribe":
                symbols = data.get("symbols", [])
                indicators = data.get("indicators", [])
                subscriptions[websocket] = {
                    "symbols": symbols,
                    "indicators": indicators
                }
                print(f"[SUBSCRIBE] Client subscribed: {symbols} | Indicators: {indicators}")
                asyncio.create_task(handle_initial_subscription(websocket, symbols, indicators))

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected.")
    finally:
        if websocket in subscriptions:
            del subscriptions[websocket]
        clients.discard(websocket)


async def websocket_handler(websocket):
    print(f"[CONNECT] Client connected")
    clients.add(websocket)
    await register_client(websocket)


async def premium_datafeed():
    uri = "ws://localhost:8001"
    print("[DATAFEED] Connecting to premium data feed via WebSocket...")

    async with websockets.connect(uri) as websocket:
        while True:
            try:
                message = await websocket.recv()
                parsed = json.loads(message)
                print(parsed)
                symbol = parsed.get("symbol_code")

                if not symbol:
                    continue

                live_tick_cache[symbol] = parsed  # update live cache

                try:
                    tick_queue.put_nowait(parsed)
                except asyncio.QueueFull:
                    print("[WARN] Tick queue full — dropping tick")

            except Exception as e:
                print(f"[ERROR] Receiving from datafeed: {e}")
                break


async def send_tick_to_clients(tick):
    symbol = tick.get("symbol_code")
    if not symbol:
        return

    # bars = get_historical_bars(symbol, timeframe)
    # if not bars:
    #     return

    for client, sub in subscriptions.items():
        if symbol not in sub["symbols"]:
            continue

        response = {
            "symbol": symbol,
            "tick": tick,
            "indicators": {}
        }

        for indicator_str in sub["indicators"]:
            try:
                parts = indicator_str.split("-")
                name = parts[0].lower()  # 'RSI' -> 'rsi'
                length = int(parts[1]) if len(parts) > 1 else None
                timeframe = parts[2] if len(parts) > 2 else None
                bars = await get_historical_bars(symbol, timeframe)
                if not bars:
                    return
                
                if name == "sma":
                    result = sma(bars, length)[-1]
                elif name == "ema":
                    result = ema(bars, length)[-1]
                elif name == "rsi":
                    result = rsi(bars,length)[-1]
                elif name == "macd":
                    macd_line, _, _ = macd(bars)
                    result = macd_line[-1]
                elif name == "supertrend":
                    super_line, direction = supertrend(bars)
                    result = {"line": super_line[-1], "dir": direction[-1]}
                else:
                    result = None
                response["indicators"][indicator_str] = result
            except Exception as e:
                response["indicators"][indicator_str] = f"error: {str(e)}"

        try:
            await client.send(json.dumps(response, default=str))
        except Exception as e:
            print(f"[ERROR] Failed to send to client: {e}")


async def dispatch_ticks():
    print('[DISPATCHER] Starting tick dispatcher...')

    while True:
        tick = await tick_queue.get()
        asyncio.create_task(send_tick_to_clients(tick))  # non-blocking


async def main():
    zmq_task = asyncio.create_task(premium_datafeed())
    dispatch_task = asyncio.create_task(dispatch_ticks())
    ws_server = await websockets.serve(
        websocket_handler, "localhost", PORT, ping_interval=20, ping_timeout=10
    )

    print(f"[SERVER] WebSocket server running at ws://localhost:{PORT}")
    await asyncio.gather(zmq_task, dispatch_task, ws_server.wait_closed())
def run_client_server():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        with open(filename, "w") as file:
            file.write(str(clients))
            file.write(str(subscriptions))
            file.write(str(tick_queue))
            file.write(str(live_tick_cache))
            file.close()
        print("[SHUTDOWN] Server stopped.")