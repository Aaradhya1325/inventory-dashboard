import asyncio
import json
import logging
from typing import Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect

from models import BinDisplayData, AlertLog, WSMessageType

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket) -> None:
        """Accept and store new WebSocket connection"""
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)
        
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")
        
        # Send connection confirmation
        await self.send_personal_message(
            websocket,
            {
                "type": WSMessageType.CONNECTION.value,
                "payload": {"message": "Connected to inventory dashboard"},
                "timestamp": datetime.now().isoformat()
            }
        )
    
    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove WebSocket connection"""
        async with self._lock:
            self.active_connections.discard(websocket)
        
        logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")
    
    async def send_personal_message(self, websocket: WebSocket, message: dict) -> None:
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
    
    async def broadcast(self, message: dict) -> None:
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        disconnected = set()
        
        async with self._lock:
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send to client: {e}")
                    disconnected.add(connection)
        
        # Remove disconnected clients
        if disconnected:
            async with self._lock:
                self.active_connections -= disconnected
    
    async def broadcast_bin_update(self, bin_data: BinDisplayData) -> None:
        """Broadcast bin update to all clients"""
        message = {
            "type": WSMessageType.BIN_UPDATE.value,
            "payload": bin_data.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(message)
        logger.debug(f"Broadcasted bin update for {bin_data.bin_id}")
    
    async def broadcast_alert(self, alert: AlertLog) -> None:
        """Broadcast alert to all clients"""
        message = {
            "type": WSMessageType.ALERT.value,
            "payload": alert.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(message)
        logger.info(f"Broadcasted alert: {alert.alert_type} for {alert.bin_id}")
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint handler"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type", "")
                
                if message_type == "ping":
                    # Respond to ping with heartbeat
                    await manager.send_personal_message(
                        websocket,
                        {
                            "type": WSMessageType.HEARTBEAT.value,
                            "payload": {"status": "ok"},
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                elif message_type == "subscribe":
                    # Could implement channel subscriptions here
                    logger.debug(f"Client subscribed to: {message.get('channel')}")
                else:
                    logger.debug(f"Unknown message type: {message_type}")
            
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received: {data}")
    
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket)
