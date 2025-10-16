import json
import aiohttp
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import Command
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CAPMONSTER_API = "https://api.capmonster.cloud"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)
user_keys = {}

# -------------------------------
# /start — main menu
# -------------------------------
@dp.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Account", callback_data="menu_account")],
        [InlineKeyboardButton(text="🧩 Captcha types", callback_data="menu_test")],
        [InlineKeyboardButton(text="⚙️ Endpoints", callback_data="menu_endpoints")]
    ])
    await message.answer(
        "👋 *Welcome to CapMonsterCloud API Playground!*\n\n"
        "Use this bot to explore and test CapMonster API methods. "
        "You can check your balance, view examples of different captcha types, "
        "or send test JSON requests.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=kb
    )

# -------------------------------
# 👤 Account menu
# -------------------------------
@dp.callback_query(F.data == "menu_account")
async def account_menu(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Enter your API key", callback_data="enter_api")],
        [InlineKeyboardButton(text="💰 Check balance", callback_data="check_balance")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_start")]
    ])
    await call.message.edit_text("👤 *Account Menu*", parse_mode=ParseMode.MARKDOWN, reply_markup=kb)

@dp.callback_query(F.data == "enter_api")
async def ask_api(call: types.CallbackQuery):
    await call.message.answer("🔑 Please send your *CapMonster API key* as a message.", parse_mode=ParseMode.MARKDOWN)

@dp.message()
async def save_api_key(message: types.Message):
    user_keys[message.from_user.id] = message.text.strip()
    await message.answer("✅ Your API key has been saved!")

@dp.callback_query(F.data == "check_balance")
async def check_balance(call: types.CallbackQuery):
    user_id = call.from_user.id
    key = user_keys.get(user_id)
    if not key:
        await call.message.answer("⚠️ Please enter your API key first (Account → Enter your API Key).")
        return

    data = {"clientKey": key}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{CAPMONSTER_API}/getBalance", json=data) as resp:
                text = await resp.text()
                result = json.loads(text)
                balance = result.get("balance")
                if balance is not None:
                    await call.message.answer(f"💰 Your current balance: *${balance:.3f}*", parse_mode=ParseMode.MARKDOWN)
                else:
                    await call.message.answer(f"❌ Error: {result.get('errorDescription', 'Unknown error')}")
    except Exception as e:
        await call.message.answer(f"❌ Connection error:\n`{e}`", parse_mode=ParseMode.MARKDOWN)

# -------------------------------
# ⚙️ Endpoints
# -------------------------------
@dp.callback_query(F.data == "menu_endpoints")
async def endpoints_menu(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 createTask", callback_data="ep_createTask")],
        [InlineKeyboardButton(text="📊 getTaskResult", callback_data="ep_getTaskResult")],
        [InlineKeyboardButton(text="💰 getBalance", callback_data="ep_getBalance")],
        [InlineKeyboardButton(text="🧾 getUserAgent", callback_data="ep_useragent_actual")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_start")]
    ])
    await call.message.edit_text("⚙️ *API Endpoints — choose a method to explore:*",
                                 parse_mode=ParseMode.MARKDOWN, reply_markup=kb)

endpoint_examples = {
    "createTask": {
        "desc": "Creates a new captcha task for CapMonster to solve.",
        "method": "POST",
        "json": {
  "clientKey": "API_KEY",
  "task": {
    "type": "RecaptchaV2Task",
    "websiteURL": "https://lessons.zennolab.com/captchas/recaptcha/v2_simple.php?level=high",
    "websiteKey": "6Lcg7CMUAAAAANphynKgn9YAgA4tQ2KI_iqRyTwd"
  },
  "callbackUrl": "https://yourwebsite.com/callback"
}
    },
    "getTaskResult": {
        "desc": "Retrieves the result of a previously created task.",
        "method": "POST",
        "json": {"clientKey": "YOUR_API_KEY", "taskId": 123456789}
    },
    "getBalance": {
        "desc": "Returns your current balance on CapMonster.Cloud.",
        "method": "POST",
        "json": {"clientKey": "YOUR_API_KEY"}
    },
    "useragent_actual": {
        "desc": "Always use a valid Windows user agent to improve captcha recognition accuracy.",
        "method": "GET",
        "json": {}
    },
}



@dp.callback_query(lambda c: c.data.startswith("ep_"))
async def show_endpoint_example(call: types.CallbackQuery):
    ep = call.data.replace("ep_", "")
    info = endpoint_examples.get(ep)

    if not info:
        await call.message.answer("❌ Unknown endpoint.")
        return

    method_url = f"{CAPMONSTER_API}/{ep.replace('_', '/')}"
    method = info.get("method", "POST")

    # if GET — without JSON, if POST — add "JSON"
    if method == "GET":
        method_text = "GET"
    else:
        method_text = "JSON POST"

    text = (
        f"📘 *{ep}*\n\n"
        f"📍 *Method URL:*\n`{method_url}`\n"
        f"📤 *Request format:* {method_text}\n\n"
        f"{info['desc']}"
    )

    # add Example
    if info.get("json") not in (None, {}):
        text += f"\n\n💡 *Example request:*\n```json\n{json.dumps(info['json'], indent=2)}\n```"

    await call.message.answer(text, parse_mode="Markdown")



# -------------------------------
# 🧩 Captcha types 
# -------------------------------
@dp.callback_query(F.data == "menu_test")
async def captcha_types_menu(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧩 RecaptchaV2Task", callback_data="test_v2")],
        [InlineKeyboardButton(text="🧠 RecaptchaV3TaskProxyless", callback_data="test_v3")],
        [InlineKeyboardButton(text="🏢 RecaptchaV2EnterpriseTask", callback_data="test_enterprise")],
        [InlineKeyboardButton(text="➕ More...", callback_data="test_more1")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_start")]
    ])
    await call.message.edit_text("🧩 *Captcha types* — explore supported captcha categories.",
                                 parse_mode=ParseMode.MARKDOWN, reply_markup=kb)

# --- Level 1 ---
@dp.callback_query(F.data == "test_more1")
async def more1(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐉 GeeTestTask", callback_data="test_geetest")],
        [InlineKeyboardButton(text="🛡️ Cloudflare TurnstileTask", callback_data="test_turnstile")],
        [InlineKeyboardButton(text="🧮 ComplexImageTask", callback_data="test_complex")],
        [InlineKeyboardButton(text="➕ More...", callback_data="test_more2")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="menu_test")]
    ])
    await call.message.edit_text("📚 *More captcha types — Level 1*", parse_mode=ParseMode.MARKDOWN, reply_markup=kb)

# --- Level 2 ---
@dp.callback_query(F.data == "test_more2")
async def more2(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔎 ComplexImageTask Recaptcha", callback_data="test_complexrec")],
        [InlineKeyboardButton(text="🖼️ ImageToTextTask", callback_data="test_imagetotext")],
        [InlineKeyboardButton(text="🧰 DataDome", callback_data="test_datadome")],
        [InlineKeyboardButton(text="➕ More...", callback_data="test_more3")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="test_more1")]
    ])
    await call.message.edit_text("📚 *More captcha types — Level 2*", parse_mode=ParseMode.MARKDOWN, reply_markup=kb)

# --- Level 3 ---
@dp.callback_query(F.data == "test_more3")
async def more3(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧧 TenDI", callback_data="test_tendi")],
        [InlineKeyboardButton(text="🛒 AmazonTask", callback_data="test_amazon")],
        [InlineKeyboardButton(text="🧬 Basilisk", callback_data="test_basilisk")],
        [InlineKeyboardButton(text="➕ More...", callback_data="test_more4")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="test_more2")]
    ])
    await call.message.edit_text("📚 *More captcha types — Level 3*", parse_mode=ParseMode.MARKDOWN, reply_markup=kb)

# --- Level 4 ---
@dp.callback_query(F.data == "test_more4")
async def more4(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧱 Imperva (Incapsula)", callback_data="test_imperva")],
        [InlineKeyboardButton(text="💹 Binance", callback_data="test_binance")],
        [InlineKeyboardButton(text="🌐 Prosopo", callback_data="test_prosopo")],
        [InlineKeyboardButton(text="➕ More...", callback_data="test_more5")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="test_more3")]
    ])
    await call.message.edit_text("📚 *More captcha types — Level 4*", parse_mode=ParseMode.MARKDOWN, reply_markup=kb)

# --- Level 5 ---
@dp.callback_query(F.data == "test_more5")
async def more5(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Temu", callback_data="test_temu")],
        [InlineKeyboardButton(text="🐼 Yidun", callback_data="test_yidun")],
        [InlineKeyboardButton(text="🔐 MTCaptcha", callback_data="test_mtcaptcha")],
        [InlineKeyboardButton(text="🧊 Altcha", callback_data="test_altcha")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="test_more4")]
    ])
    await call.message.edit_text("📚 *More captcha types — Level 5*", parse_mode=ParseMode.MARKDOWN, reply_markup=kb)

# -------------------------------
# 📄 Example
# -------------------------------
captcha_examples = {
    "test_v2": {
        "type": "RecaptchaV2Task",
        "request": {
  "clientKey":"API_KEY",
  "task": {
	"type":"RecaptchaV2Task",
	"websiteURL":"https://lessons.zennolab.com/captchas/recaptcha/v2_simple.php?level=high",
	"websiteKey":"6Lcg7CMUAAAAANphynKgn9YAgA4tQ2KI_iqRyTwd"
  }
},
        "response": {
            "errorId": 0,
            "taskId": 123456789
        }
    },
    "test_v3": {
        "type": "RecaptchaV3TaskProxyless",
        "request": {
            "clientKey": "API_KEY",
            "task": {
                "type": "RecaptchaV3TaskProxyless",
                "websiteURL": "https://lessons.zennolab.com/captchas/recaptcha/v3.php?level=beta",
                "websiteKey": "6Le0xVgUAAAAAIt20XEB4rVhYOODgTl00d8juDob",
                "minScore": 0.3,
                "pageAction": "myverify"
            }
        },
        "response": {
            "errorId": 0,
            "taskId": 987654321
        }
    },
    "test_enterprise": {
        "type": "RecaptchaV2EnterpriseTask",
        "request": {
            "clientKey": "API_KEY",
            "task": {
                "type": "RecaptchaV2EnterpriseTask",
                "websiteURL": "https://mydomain.com/page-with-recaptcha-enterprise",
                "websiteKey": "6Lcg7CMUAAAAANphynKgn9YAgA4tQ2KI_iqRyTwd",
                "enterprisePayload": {"s": "SOME_ADDITIONAL_TOKEN"}
            }
        },
        "response": {
            "errorId": 0,
            "taskId": 543219876
        }
    },
    "test_geetest": {
        "type": "GeeTestTask",
        "request": {
	"clientKey":"YOUR_CAPMONSTER_CLOUD_API_KEY",
	"task":
	{
		"type":"GeeTestTask",
		"websiteURL":"https://www.geetest.com/en/demo",
		"gt":"022397c99c9f646f6477822485f30404",
		"challenge":"7f044f48bc951ecfbfc03842b5e1fe59",
		"geetestApiServerSubdomain":"api-na.geetest.com"

	}
},
        "response": {
            "errorId": 0,
            "taskId": 246810121
        }
    },
    "test_turnstile": {
        "type": "TurnstileTaskProxyless",
        "request": {
  "clientKey": "API_KEY",
  "task": {
    "type": "TurnstileTask",
    "websiteURL": "http://tsmanaged.zlsupport.com",
    "websiteKey": "0x4AAAAAAABUYP0XeMJF0xoy"
  }
},
        "response": {
            "errorId": 0,
            "taskId": 135791113
        }
    },
    "test_complex": {
        "type": "ComplexImageTask",
        "request": {
	"clientKey": "API_KEY",
	"task": {
		"type": "ComplexImageTask",
		"class": "recognition",
		"imagesBase64": [
			"{background_base64}",
			"{circle_base64}"
		],
		"metadata": {
			"Task": "oocl_rotate_new"
		}
	}
},
        "response": {
            "errorId": 0,
            "taskId": 135791113
        }
    },
    "test_complexrec": {
        "type": "ComplexImageTask",
        "request": {
  "clientKey":"API_KEY",
  "task": {
	"type": "ComplexImageTask",
	"class": "recaptcha",
	"imageUrls":[ "https://i.postimg.cc/yYjg75Kv/payloadtraffic.jpg" ],
	"metadata": {
	  "Task": "Click on traffic lights",
	  "Grid": "3x3",
	  "TaskDefinition": "/m/015qff"
	},
	"userAgent": "userAgentPlaceholder",
	"websiteUrl": "https://lessons.zennolab.com/captchas/recaptcha/v2_simple.php?level=middle"
  }
},
        "response": {
            "errorId": 0,
            "taskId": 135791113
        }
    },
    "test_imagetotext": {
        "type": "ImageToTextTask",
        "request": {
  "clientKey":"API_KEY",
  "task": {
	"type":"ImageToTextTask",
	"body":"BASE64_BODY_HERE!"
  }
},
        "response": {
            "errorId": 0,
            "taskId": 135791113
        }
    },
    "test_datadome": {
        "type": "DataDome",
        "request": {
  "clientKey": "API_KEY",
  "task": {
    "type": "CustomTask",
    "class": "DataDome",
    "websiteURL": "https://example.com",
    "userAgent": "userAgentPlaceholder",
    "metadata": {
      "captchaUrl": "https://geo.captcha-delivery.com/interstitial/?initialCid=AHrlqAAAAAMA9UvsL58YLqIAXNLFPg%3D%3D&hash=C0705ACD75EBF650A07FF8291D3528&cid=7sfa5xUfDrR4bQTp1c2mhtiD7jj9TXExcQypjdNAxKVFyIi1S9tE0~_mqLa2EFpOuzxKcZloPllsNHjNnqzD9HmBA4hEv7SsEyPYEidCBvjZEaDyfRyzefFfolv0lAHM&referer=https%3A%2F%2Fwww.example.com.au%2F&s=6522&b=978936&dm=cm",
      "datadomeCookie": "datadome=VYUWrgJ9ap4zmXq8Mgbp...64emvUPeON45z"
    },
    "proxyType": "http",
    "proxyAddress": "123.45.67.89",
    "proxyPort": 8080,
    "proxyLogin": "proxyUsername",
    "proxyPassword": "proxyPassword"
  }
},
        "response": {
            "errorId": 0,
            "taskId": 135791113
        }
    },
    "test_tendi": {
        "type": "TenDI",
        "request": {
  "clientKey": "API_KEY",
  "task": {
    "type": "CustomTask",
    "class": "TenDI",
    "websiteURL": "https://example.com",
    "websiteKey": "189123456",
    "userAgent": "userAgentPlaceholder",
    "metadata": {
      "captchaUrl": "https://global.captcha.example.com/TCaptcha-global.js"
    }
  }
},
        "response": {
            "errorId": 0,
            "taskId": 135791113
        }
    },
    "test_amazon": {
        "type": "AmazonTask",
        "request": {
  "clientKey": "API_KEY",
  "task": {
    "type": "AmazonTask",
    "websiteURL": "https://example.com/index.html",
    "websiteKey": "h15hX7brbaRTR...Za1_1",
    "userAgent": "userAgentPlaceholder",
    "captchaScript": "https://234324vgvc23.yejk.captcha-sdk.awswaf.com/234324vgvc23/jsapi.js",
    "cookieSolution": "true"
  }
},
        "response": {
            "errorId": 0,
            "taskId": 135791113
        }
    },
    "test_basilisk": {
        "type": "Basilisk",
        "request": {
  "clientKey": "API_KEY",
  "task": {
    "type": "CustomTask",
    "class": "Basilisk",
    "websiteURL": "https://domain.io/account/register",
    "websiteKey": "b7890hre5cf2544b2759c19fb2600897",
    "userAgent": "userAgentPlaceholder"
  }
},
        "response": {
            "errorId": 0,
            "taskId": 135791113
        }
    },
    "test_imperva": {
        "type": "Imperva",
        "request": {
  "clientKey": "API_KEY",
  "task": {
    "type": "CustomTask",
    "class": "Imperva",
    "websiteURL": "https://example.com",
    "userAgent": "userAgentPlaceholder",
    "metadata": {
      "incapsulaScriptUrl": "_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3",
      "incapsulaCookies": "incap_ses_1166_2930313=br7iX33ZNCtf3HlpEXcuEDzz72cAAAAA0suDnBGrq/iA0J4oERYzjQ==; visid_incap_2930313=P3hgPVm9S8Oond1L0sXhZqfK72cAAAAAQUIPAAAAAABoMSY9xZ34RvRseJRiY6s+;",
      "reese84UrlEndpoint": "Built-with-the-For-hopence-Hurleysurfecting-the-"
    }
  }
},
        "response": {
            "errorId": 0,
            "taskId": 135791113
        }
    },
    "test_binance": {
        "type": "BinanceTask",
        "request": {
	"clientKey": "API_KEY",
	"task": 
	{
		"type": "BinanceTask",
		"websiteURL": "https://example.com",
		"websiteKey": "login",
		"validateId": "cb0bfefa598b4c3887661fde54ecd57b",
		"userAgent": "userAgentPlaceholder"
	}
},
        "response": {
            "errorId": 0,
            "taskId": 135791113
        }
    },
    "test_prosopo": {
        "type": "ProsopoTask",
        "request": {
	"clientKey": "API_KEY",
	"task": 
	{
		"type": "ProsopoTask",
		"websiteURL": "https://www.example.com",
		"websiteKey": "5EZU3LG31uzq1Mwi8inwqxmfvFDpj7VzwDnZwj4Q3syyxBwV"
	}
},
        "response": {
            "errorId": 0,
            "taskId": 135791113
        }
    },
    "test_temu": {
        "type": "Temu",
        "request": {
  "clientKey": "API_KEY",
  "task": {
    "type": "CustomTask",
    "class": "Temu",
    "websiteURL": "https://www.example.com/bgn_verification.html?verifyCode=7PRQIzDznoFE67ecZYtRTw394f6185143a4af80&from=https%3A%2F%2Fwww.example.com%2F&refer_page_name=home&refer_page_id=10005_1743074140645_cwb6un82rq&refer_page_sn=10005&_x_sessn_id=xmp1zuyv7y",
    "userAgent": "userAgentPlaceholder",
    "metadata": {
      "cookie": "region=141; language=en; currency=EUR; api_uid=CnBpI2fwFW2BogBITHVYAg==; timezone=Europe%2FMoscow; _nano_fp=XpmYXqmJnqX8npXblT_T6~7rkpA2LDnz2BPFuT5m; privacy_setting_detail=%7B%22firstPAds%22%3A0%2C%22adj%22%3A0%2C%22fbsAnlys%22%3A0%2C%22fbEvt%22%3A0%2C%22ggAds%22%3A0%2C%22fbAds%22%3A0%2C%22ttAds%22%3A0%2C%22scAds%22%3A0%2C%22ptAds%22%3A0%2C%22bgAds%22%3A0%2C%22tblAds%22%3A0%2C%22obAds%22%3A0%2C%22vgAds%22%3A0%2C%22idAds%22%3A0%2C%22opAds%22%3A0%2C%22stAds%22%3A0%2C%22pmAds%22%3A0%7D; webp=1; _bee=pgoBlKp038lBhEyoQ4yXnuNrw1X5va2U; verifyAuthToken=QkZmx2TJFbSuuRVD_MKJmA0b84fe3df183da8ab"
    }
  }
},
        "response": {
            "errorId": 0,
            "taskId": 135791113
        }
    },
    "test_yidun": {
        "type": "YidunTask",
        "request": {
  "clientKey": "API_KEY",
  "task": {
    "type": "YidunTask",
    "websiteURL": "https://www.example.com",
    "websiteKey": "6cw0f0485d5d46auacf9b735d20218a5",
    "userAgent": "userAgentPlaceholder"
  }
},
        "response": {
            "errorId": 0,
            "taskId": 135791113
        }
    },
    "test_mtcaptcha": {
        "type": "MTCaptchaTask",
        "request": {
  "clientKey": "API_KEY",
  "task": 
  {
    "type": "MTCaptchaTask",
    "websiteURL": "https://www.example.com",
    "websiteKey": "MTPublic-abCDEFJAB",
    "isInvisible": "false",
    "pageAction": "login"
  }
},
        "response": {
            "errorId": 0,
            "taskId": 135791113
        }
    },
    "test_altcha": {
        "type": "altcha",
        "request": {
  "clientKey": "API_KEY",
  "task": {
    "type": "CustomTask",
    "class": "altcha",
    "websiteURL": "https://example.com",
    "websiteKey": "",
    "userAgent": "userAgentPlaceholder",
    "metadata": {
      "challenge": "3dd28253be6cc0c54d95f7f98c517e68744597cc6e66109619d1ac975c39181c",
      "iterations": "5000",
      "salt": "bf356449d56c719fd904c58f",
      "signature": "4b1cf0e0be0f4e5247e50b0f9a449830f1fbca44c32ff94bc080146815f31a18"
    }
  }
},
        "response": {
            "errorId": 0,
            "taskId": 135791113
        }
    },

}


@dp.callback_query(F.data.startswith("test_"))
async def show_captcha_example(call: types.CallbackQuery):
    key = call.data
    if key not in captcha_examples:
        return await call.answer("⚠️ Example not yet added.")
    
    example = captcha_examples[key]
    text = (
        f"🧩 *{example['type']}*\n\n"
        f"📍 *Method URL:*\n`https://api.capmonster.cloud/createTask`\n"
        f"📤 *Request format:* JSON POST\n\n"
        f"💡 *Example request:*\n```json\n{json.dumps(example['request'], indent=2)}\n```\n\n"
        f"📥 *Example response:*\n```json\n{json.dumps(example['response'], indent=2)}\n```"
    )
    await call.message.answer(text, parse_mode=ParseMode.MARKDOWN)


# -------------------------------
# Back to start
# -------------------------------
@dp.callback_query(F.data == "back_start")
async def back_to_start(call: types.CallbackQuery):
    await start(call.message)

# -------------------------------
# RUN
# -------------------------------
async def main():
    print("🚀 Bot started successfully!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
