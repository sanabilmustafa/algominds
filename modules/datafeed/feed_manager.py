import asyncio
import zmq
import zmq.asyncio
import websockets
import json
from .utils import parse_feed
from .parsers import parse_mbo, parse_mbp

connected_clients = set()

async def zmq_listener():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:15012")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")

    print("Connected to raw ZMQ data feed")

    while True:
        try:
            msg = await socket.recv_string()
            parsed = parse_feed(msg)
            print(parsed)
            if parsed:
                await broadcast(parsed)
        except Exception as e:
            print(f"[ZMQ ERROR] {e}")

async def broadcast(data):
    message = json.dumps(data, default=str)
    for client in connected_clients.copy():
        try:
            await client.send(message)
            print(f"[+] Sent to client: {message}")
        except Exception as e:
            print(f"[ERROR] Sending to client: {e}")
            connected_clients.remove(client)

async def handle_ws_client(websocket):
    print(f"[+] Premium client connected")
    connected_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)
        print(f"[-] Premium client disconnected")

async def main():
    ws_server = await websockets.serve(handle_ws_client, "localhost", 8001)
    await zmq_listener()

def run_datafeed():
    asyncio.run(main())
