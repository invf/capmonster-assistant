# 🧠 CapMonster Cloud — Assistant

An interactive demo project that helps users understand and test how the **[CapMonster.Cloud API](https://capmonster.cloud/)** works.

This project includes two main components:
1. **🌐 Web UI (CapMonster Assistant)** — a modern dashboard for checking your API balance and viewing captcha-solving demos.  
2. **🤖 Telegram Bot (CapMonster API Explorer)** — an interactive bot that allows you to explore API endpoints, send example requests, and test captcha-solving tasks directly in Telegram.

---

## 🌐 Web UI — CapMonster Assistant

### 🔗 Live demo:
👉 [https://capmonster-assistant.vercel.app/](https://capmonster-assistant.vercel.app/)

### 🧩 Features
- Enter your **CapMonster API key** to check your current balance in real time  
- See **how many captchas** of each type can be solved with your current balance  
- Explore detailed **demo examples** for 16+ captcha types (ReCaptcha V2, V3, Enterprise, Turnstile, GeeTest, DataDome, etc.)  
- Responsive design — optimized for both desktop and mobile devices  
- Integrated with Telegram Mini App  

### ⚙️ Technologies
- Frontend: **HTML, CSS, JavaScript**
- Backend: **FastAPI (Python, aiohttp, CORS middleware)**
- Hosting:  
  - Backend — **Render**  
  - Frontend — **Vercel**

### 🖥️ Run locally
```bash
# 1️⃣ Clone the repository
git clone https://github.com/invf/capmonster-assistant.git
cd capmonster-assistant

# 2️⃣ Backend setup
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# 3️⃣ Frontend setup
cd ../frontend
python -m http.server 8080

🤖 Telegram Bot — CapMonster API Explorer

The bot acts like a mini Postman for CapMonster.Cloud — allowing users to test API requests, see example JSONs, and understand how each endpoint works.

✨ Key Features

/start — Greeting and introduction

📂 Account menu:

Enter your API key
Check your balance in real time
⚙️ Endpoints menu:

createTask
getTaskResult
getBalance
getUserAgent
Each shows example request/response formats

🧩 Captcha types testing:
Explore ready-made examples for all supported captcha types:
ReCaptchaV2Task
ReCaptchaV3TaskProxyless
ReCaptchaV2EnterpriseTask
GeeTestTask
Cloudflare TurnstileTask
ComplexImageTask
ImageToTextTask
DataDome, TenDI, AmazonTask, Basilisk, Imperva, Binance, Prosopo, Temu, Yidun, MTCaptcha, Altcha, and more
Realistic demo examples of requests and responses formatted in JSON
⚙️ Technologies
Python 3.10+
Aiogram 3.x
Dotenv
Render (bot hosting)

🧾 Environment Variables
Create a .env file inside the /bot folder:
BOT_TOKEN=your_telegram_bot_token
CAPMONSTER_API=https://api.capmonster.cloud

▶️ Run locally
cd bot
python bot.py

📦 Project structure
capmonster-assistant/
│
├── backend/
│   ├── main.py              # FastAPI backend
│   └── requirements.txt
│
├── frontend/
│   ├── index.html           # Web UI dashboard
│   ├── prices.json          # Captcha type pricing
│   └── gifs/                # Demo GIFs for captchas
│
├── bot/
│   ├── bot.py               # Telegram Bot
│   └── .env.example
│
└── README.md

🧩 Future ideas

Integration with user’s CapMonster account analytics
Add AI-based task suggestions for best captcha type
Real-time dashboard synchronization between Web UI and Telegram Bot
Browser extension to auto-fetch tokens and send to CapMonster API
📬 Author
Developed by: @invf
Project site: capmonster-assistant.vercel.app
Telegram contact: @zennoguru