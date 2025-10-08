from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import aiohttp, json

app = FastAPI()

origins = [
    "http://localhost:8080",                
    "http://127.0.0.1:8080",
    "https://capmonster-assistant.vercel.app" 
]

# Allowing the frontend to access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CAP_URL = "https://api.capmonster.cloud/getBalance"

@app.post("/get_balance")
async def get_balance(clientKey: str = Form(...)):
    """
    Accepts API key, makes a request to CapMonster, returns balance.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(CAP_URL, json={"clientKey": clientKey}) as resp:
            text = await resp.text()
            try:
                # first we try to parse plain JSON
                data = await resp.json()
            except Exception:
                try:
                    # if CapMonster returned JSON as a string — let's parse it again
                    data = json.loads(text)
                except Exception:
                    # if it didn't work at all — we return the raw text
                    data = {"error": "Unexpected response", "raw": text, "status": resp.status}
    return data


@app.get("/ping")
async def ping():
    return {"status": "ok"}
