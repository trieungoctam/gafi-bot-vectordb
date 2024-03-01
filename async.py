from fastapi.responses import StreamingResponse
import os
from typing import AsyncGenerator
from fastapi import FastAPI
import httpx

API_KEY = os.environ["OPENAI_API_KEY"]
TIMEOUT = 30

app = FastAPI()

data = {
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "Generate name of 100 animals"
      }
    ],
    "stream": True
}

# async def openai_stream() -> AsyncGenerator[str, None]:
#     async with httpx.AsyncClient(timeout=httpx.Timeout(TIMEOUT)) as client:
#         async with client.stream(
#             "POST",
#             "https://api.openai.com/v1/chat/completions",
#             headers={
#                 "Authorization": f"Bearer {API_KEY}",
#             },
#             json=data,
#         ) as response:
#             print(f"received response status_code={response.status_code}")
#             # response.raise_for_status(
#             async for chunk in response.aiter_bytes():
#                 print(chunk)
#                 yield chunk

@app.get("/")
# async def post():
#     return StreamingResponse(openai_stream(), media_type="text/event-stream")
async def openai_stream():
    async with httpx.AsyncClient(timeout=httpx.Timeout(TIMEOUT)) as client:
        async with client.stream(
            "POST",
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
            },
            json=data,
        ) as response:
            print(f"received response status_code={response.status_code}")
            async for chunk in response.aiter_text(None):
                print(chunk)
                yield chunk

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)