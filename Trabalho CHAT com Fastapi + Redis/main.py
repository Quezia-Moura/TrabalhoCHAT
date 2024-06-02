import aioredis
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from typing import List

app = FastAPI()

clients: List[WebSocket] = []

async def get_redis_connection():
    return await aioredis.create_redis_pool("redis://127.0.0.1:6379")

@app.get("/")
async def get():
    return FileResponse("index.html")

@app.get("/styles.css")
async def get_css():
    return FileResponse("styles.css")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    
    redis = await get_redis_connection() 
    
    try:
        while True:
            data = await websocket.receive_text()
            
            await redis.lpush("chat_messages", data)
            
            for client in clients:
                if client != websocket:
                    await client.send_text(f"FULANO: {data}")
                else:
                    await client.send_text(f"VOCÊ: {data}")
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        clients.remove(websocket)
        redis.close()
        await redis.wait_closed()
