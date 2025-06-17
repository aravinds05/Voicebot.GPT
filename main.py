from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
import openai

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve HTML templates
templates = Jinja2Templates(directory="templates")

# Static files (optional)
#app.mount("/static", StaticFiles(directory="static"), name="static")

# Request model
class ChatRequest(BaseModel):
    message: str
    api_key: str
@app.get("/")
def root():
    return {"message": "Backend running"}
# Home page (index)
@app.get("/index")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Voicebot page
@app.get("/voicebot")
def voicebot_page(request: Request):
    return templates.TemplateResponse("voicebot.html", {"request": request})

# Chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        print(f"Received message: {request.message}") 
    
        client = OpenAI(api_key=request.api_key)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a compassionate and slightly humorous voice assistant. Use a warm and patient tone."},
                {"role": "user", "content": request.message}
            ]
        )
        return {"response": response.choices[0].message.content}

    except openai.RateLimitError:
        return JSONResponse(
            status_code=429,
            content={"error": "OpenAI API quota exceeded. Please check your plan or try again later."}
        )
    
    except openai.AuthenticationError:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid API key. Please enter a valid key."})
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Unexpected server error: {str(e)}" }
        )