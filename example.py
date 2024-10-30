import asyncio
from time import time
from websocket_rooms import Room
from fastapi import Depends, FastAPI, WebSocket
from typing import Any, NoReturn
import logging
from fastapi.responses import HTMLResponse

html = """"
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
        <style>
            /* Đặt chiều cao cho khung chat và khung tin nhắn */
            body {
                font-family: Arial, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }
            h1 {
                margin-bottom: 20px;
            }
            #chatContainer {
                display: flex;
                flex-direction: column;
                width: 100%;
                max-width: 600px;
                height: 80vh;
                border: 1px solid #ccc;
                border-radius: 8px;
                overflow: hidden;
            }
            #messages {
                flex-grow: 1;
                overflow-y: auto;
                padding: 10px;
                border-bottom: 1px solid #ccc;
            }
            #messages li {
                list-style-type: none;
                margin-bottom: 10px;
            }
            #inputContainer {
                display: flex;
                padding: 10px;
            }
            #messageText {
                flex-grow: 1;
                padding: 8px;
                font-size: 16px;
                border: 1px solid #ccc;
                border-radius: 4px;
                margin-right: 10px;
            }
            button {
                padding: 8px 16px;
                font-size: 16px;
                border: none;
                border-radius: 4px;
                background-color: #4CAF50;
                color: white;
                cursor: pointer;
            }
            button:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <h1>Time WebSocket</h1>
        <div id="chatContainer">
            <ul id="messages">
            </ul>
            <div id="inputContainer">
                <input type="text" id="messageText" autocomplete="off" placeholder="Nhập tin nhắn..."/>
                <button onclick="sendMessage(event)">Gửi</button>
            </div>
        </div>
        <script>
            var ws = new WebSocket("ws://localhost:8000/current_time");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages');
                var message = document.createElement('li');
                var content = document.createTextNode(event.data);
                message.appendChild(content);
                messages.appendChild(message);
                messages.scrollTop = messages.scrollHeight; // Tự động cuộn xuống cuối khung tin nhắn
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText");
                if (input.value.trim() !== "") {
                    ws.send(input.value);
                    input.value = '';
                }
                event.preventDefault();
            }
        </script>
    </body>
</html>
"""

app = FastAPI()

@app.get("/")
async def get():
    return HTMLResponse(html)

time_room = Room()

@time_room.on_receive("text")
async def on_receive(room: Room, websocket: WebSocket, message: Any) -> None:
    print("{}:{} just sent '{}'".format(websocket.client.host, websocket.client.port, message))
    await room.push_text(f"{websocket.client.host}: {message}")
@time_room.on_connect("after")
async def on_chatroom_connection(room: Room, websocket: WebSocket) -> None:
    print("{}:{} joined the channel".format(websocket.client.host, websocket.client.port))

@time_room.on_disconnect("after")
async def on_chatroom_disconnect(room: Room, websocket: WebSocket) -> None:
    print("{}:{} left the channel".format(websocket.client.host, websocket.client.port))

# async def updater_function(room: Room) -> NoReturn:
#     while True:
#         t = time()
#         await room.push_json({"current_time": t})
#         await asyncio.sleep(1)
#
# updater_task = asyncio.create_task(updater_function(time_room))

@app.websocket("/current_time")
async def connect_websocket(websocket: WebSocket, room: Room = Depends(time_room)):
    await room.connect(websocket)
