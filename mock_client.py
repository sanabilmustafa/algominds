# mock_client.py

import asyncio
import websockets
import json

# Replace with your actual WebSocket server URL
# TICK_URL = "ws://localhost:5556"
# IND_URL = "ws://localhost:5557"
WS_URL = 'ws://localhost:8765'

async def subscribe_and_receive():
    async with websockets.connect(WS_URL) as websocket:
        print("Connected to WebSocket server!")

        # Placeholder for sending subscription request (optional/future)
        await websocket.send(json.dumps({
            "action": "subscribe",
            "symbols": ["SYS", "OGDC"],
            "indicators": ["sma", "ema"]
        }))
        print("Subscribed to symbols.")

        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                print("\n📥 Received message:")
                print(json.dumps(data, indent=2))
        except websockets.ConnectionClosed:
            print("WebSocket connection closed")

if __name__ == "__main__":
    asyncio.run(subscribe_and_receive())
