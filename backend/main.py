import os, time, base64, requests
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(".env.backend")
API_KEY = os.getenv("CAPMONSTER_API_KEY")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/solve")
async def solve(file: UploadFile = File(...)):
    body = base64.b64encode(await file.read()).decode()
    task = {"clientKey": API_KEY, "task": {"type": "ImageToTextTask", "body": body}}
    create = requests.post("https://api.capmonster.cloud/createTask", json=task).json()
    task_id = create.get("taskId")

    # опитування результату
    while True:
        res = requests.post(
            "https://api.capmonster.cloud/getTaskResult",
            json={"clientKey": API_KEY, "taskId": task_id}
        ).json()
        if res.get("status") == "ready":
            return {"status": "ready", "solution": {"type": "image", "text": res["solution"]["text"]}}
        time.sleep(2)
