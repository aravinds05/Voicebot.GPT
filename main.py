from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import openai
from openai import OpenAI  #groq
import os #secure api key

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

class ChatRequest(BaseModel):
    message: str

@app.get("/")
@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/index")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/voicebot")
def voicebot_page(request: Request):
    return templates.TemplateResponse("voicebot.html", {"request": request})

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        print(f"Received message: {request.message}") 

        client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),  
            base_url="https://api.groq.com/openai/v1"
        )

        response = client.chat.completions.create(
            model="llama3-70b-8192",  
            messages=[
                {"role": "system", "content": "You are a compassionate and slightly humorous voice assistant. Use a warm and patient tone."},
                {"role": "user", "content": request.message}
            ]
        )
        return {"response": response.choices[0].message.content}

    except openai.RateLimitError:
        return JSONResponse(
            status_code=429,
            content={"error": "Groq API quota exceeded. Please check your plan or try again later."}
        )
    
    except openai.AuthenticationError:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid Groq API key. Please enter a valid key."})
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Unexpected server error: {str(e)}" })
