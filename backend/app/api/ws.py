"""
WebSocket endpoint for live dashboard updates. Clients connect here
and receive real-time events (new tickets, risk score changes)
published via Redis pub/sub — decoupling the event source from the
delivery mechanism, so this scales cleanly to multiple backend
instances later.
"""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.redis_client import redis_client

router = APIRouter()

CHANNEL = "ticket_events"


@router.websocket("/ws/tickets")
async def ticket_events_ws(websocket: WebSocket):
    await websocket.accept()
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(CHANNEL)

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                await websocket.send_text(message["data"])
            # Small sleep prevents a tight busy-loop when no messages arrive
            await asyncio.sleep(0.05)
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(CHANNEL)
        await pubsub.close()


async def publish_ticket_event(event_type: str, ticket_data: dict):
    """
    Called from ticket creation/update/risk-scoring routes to notify
    all connected dashboards of a change, in real time.
    """
    payload = json.dumps({"event": event_type, "data": ticket_data})
    await redis_client.publish(CHANNEL, payload)