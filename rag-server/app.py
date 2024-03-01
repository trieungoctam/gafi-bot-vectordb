from fastapi import FastAPI
from typing import List, Dict, Any
from fastapi import Request, HTTPException, Response
from datetime import datetime
from config import special_instructions
from json import loads
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


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHROMA_PATH = "../chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
Detailed and well-thought-out answers
"""

embedding_function = OpenAIEmbeddings()
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

def get_gpt_response(conversation, model):
    # stream = ChatOpenAI().invoke(data['prompt'])
    url = 'http://127.0.0.1:11001/openai'

    json={
            "model": model,
            "messages": conversation
        }
    

    with requests.post(url, stream=True, json = json) as r:
        for chunk in r.iter_content(None):
            print(chunk)
            yield chunk

@app.post("/rag")
async def _conversation(request: Request):
        try:
            req_json = await request.json()
            jailbreak = req_json["jailbreak"]
            # internet_access = req_json["meta"]["content"]["internet_access"]
            _conversation = req_json["meta"]["content"]["conversation"]
            prompt = req_json["meta"]["content"]["parts"][0]
            current_date = datetime.now().strftime("%Y-%m-%d")
            system_message = f"""
                You are a helpful, friendly and informative assistant. 
                If the user say hi or hello, you can say hi back and introduce yourself as 'GameFi Assistant'.
                If the context is not empty, then the context is the information you have about the user's question. 
                Use that information and the topic of the question to generate an informative response.
                If user ask a question and the context is empty, then you say you dont know. 
                !!! Do not say that you answer the question with the context, just answer the question.
            """

            results = db.similarity_search_with_relevance_scores(prompt['content'], k=3)
    
            context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
            prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
            
            if (len(results) > 0):
                prompt['content'] = prompt_template.format(context=context_text, question=prompt['content'])

            model = req_json['model']
            model = "gpt-3.5-turbo-0125"

            conversation = (
                [{"role": "system", "content": system_message}]
                + special_instructions[jailbreak]
                + _conversation
                + [prompt]
            )

            return StreamingResponse(get_gpt_response(conversation, model), media_type='text/event-stream')

        except Exception as e:
            print(e)
            print(e.__traceback__.tb_next)
            raise HTTPException(status_code=400, detail={
                "_action": "_ask",
                "success": False,
                "error": f"an error occurred: {str(e)}"
            })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=2163)