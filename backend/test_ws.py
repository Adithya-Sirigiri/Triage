"""
Simple standalone script to test the WebSocket connection and
Redis pub/sub pipeline, without needing a browser.
"""
import asyncio
import websockets

async def test():
    uri = "ws://localhost:8000/ws/tickets"
    async with websockets.connect(uri) as websocket:
        print("Connected! Waiting for events...")
        print("(Now create a ticket via /docs in another terminal/tab)")
        async for message in websocket:
            print(f"Received: {message}")

asyncio.run(test())