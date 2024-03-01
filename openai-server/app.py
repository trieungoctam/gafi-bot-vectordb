from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from httpx import AsyncClient, HTTPStatusError
from typing import AsyncGenerator
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import os
import openai
import uvicorn

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_openai_generator(data: Dict[str, str]):
  
    stream = llm.chat.completions.create(
        model=data['model'],
        messages=data['messages'],
        stream=True,
        temperature=1,
        top_p=0.95
    )
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if  content is not None:
            print(content)
            yield content


@app.post("/openai")
async def chat_open_ai(request: Request):
    req_json = await request.json()
    return StreamingResponse(get_openai_generator(req_json), media_type='text/event-stream')

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=11001)