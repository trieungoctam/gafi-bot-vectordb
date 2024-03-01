import requests
from dataclasses import dataclass
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from httpx import AsyncClient, HTTPStatusError
from typing import AsyncGenerator
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embedding_function = OpenAIEmbeddings()
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

def get_gpt_response(prompt: str):
    # stream = ChatOpenAI().invoke(data['prompt'])
    url = 'http://127.0.0.1:8000/openai'

    data = {
                "model": "gpt-3.5-turbo",
                "conversation": [
                    {
                        "role": "system",
                        "content": "You are ChatGPT also known as ChatGPT, a large language model trained by OpenAI. Strictly follow the users instructions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

    with requests.post(url, stream=True, json = data) as r:
        for line in r.iter_lines():
            if line is not None:
                line = line.decode('utf-8')
                print(line)
                yield line

@app.post("/rag")
async def get_vectorstore(request: Request):
    req_json = await request.json()
    query_text = req_json['query_text']

    results = db.similarity_search_with_relevance_scores(query_text, k=5)
    # if len(results) == 0 or results[0][1] < 0.7:
    #     raise HTTPException(status_code=404, detail="Unable to find matching results.")
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    
    return StreamingResponse(get_gpt_response(prompt), media_type='text/event-stream')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=2163)