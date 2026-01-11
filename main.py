from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Корневой маршрут для проверки
@app.get("/")
def home():
    return {"status": "OK", "message": "Telegram Shop Backend is running!"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    body = await request.json()

    if 'message' in body and 'web_app_data' in body['message']:
        user = body['message']['from']
        chat_id = user['id']
        web_app_data_str = body['message']['web_app_data']['data']

        try:
            data = json.loads(web_app_data_str)
            cart = data.get("cart", [])
            total = sum(item["price"] for item in cart)

            message = (
                f"💖 Спасибо за заказ!\n"
                f"Сумма: {total} ₽\n\n"
                f"Переведите по СБП на номер:\n"
                f"📱 +7 (999) 123-45-67 (Тинькофф)\n\n"
                f"После перевода напишите «Оплатил» — отправим товар!\n\n"
                f"Ваш заказ:\n"
            )
            for item in cart:
                message += f"• {item['name']}\n"

            bot_token = os.getenv("BOT_TOKEN")
            if not bot_token:
                print("❌ BOT_TOKEN не задан!")
                return {"error": "BOT_TOKEN missing"}

            # ИСПРАВЛЕНО: убран пробел после 'bot'
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            response = requests.post(url, json={"chat_id": chat_id, "text": message})

            if response.status_code != 200:
                print("❌ Ошибка Telegram API:", response.text)

            print(f"✅ Заказ от @{user.get('username', chat_id)} на {total} ₽")
            return {"ok": True}

        except Exception as e:
            print("❌ Ошибка:", e)
            return {"error": str(e)}

    return {"ok": True}