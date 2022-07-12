# Websocket Rooms: `websocket_rooms`

A python library for creating WebSocket rooms, for message sharing or data distribution to multiple connections.

This library was created after building a several real-time web apps and implementing the same mechanisem to broadcast real-time messages between clients listening for the same real-time telemetries.
The library simplifies the solution for this issue, and proposes a simpler way to handle multiple websocket clients that act the same way.

## Basic use:
Let's create a chatroom where everyone can post their messages:
```python
from websocket_rooms import Room

chat_room = Room()

@chat_room.on_receive("json")
async def on_receive(room: Room, websocket: WebSocket, message: Any) -> None:
    await room.push(message)

@chat_room.on_connection
async def on_chatroom_connection(room: Room, websocket: WebSocket) -> None:
    logging.info("{} joined the chat room".format(websocket.client.host))

@chat_app.websocket("/chat")
async def connect_websocket(websocket: WebSocket):
    await chat_room.connect(websocket)
```
## More advanced usage

Example of a more advanced use case, with modification to the `Room` base class:
Suppose a class `RoomWithClientId`, where each WebSocket has a `client_id` associated with it, which it receives on connection:
```python
class RoomWithClientId(Room):
    def __init__(self, base_room: Optional[BaseRoom] = None) -> None:
        super().__init__(base_room)
        self._id_to_ws = {}

    async def connect(self, websocket: WebSocket, client_id: int) -> None:
        self._id_to_ws[websocket] = client_id
        await super().connect(websocket)

    def get_client_id(self, websocket: WebSocket) -> int:
        return self._id_to_ws.get(websocket)


chat_room = RoomWithClientId()

@chat_room.on_receive("json")
async def on_chatroom_receive(room: RoomWithClientId, websocket: WebSocket, message: Any) -> None:
    await room.push(message)

@chat_room.on_connection
async def on_chatroom_connection(room: RoomWithClientId, websocket: WebSocket, client_id: int) -> None:
    logging.info("{} joined the chat room".format(client_id))

@app.websocket("/chat/{client_id}")
async def connect_websocket(websocket: WebSocket, client_id: int):
    await chat_room.connect(websocket, client_id)
```
