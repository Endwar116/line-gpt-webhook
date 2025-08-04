import os
import openai
from openai import OpenAI
from fastapi import FastAPI, Request
from pydantic import BaseModel
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
from roles import get_prompt, available_roles

app = FastAPI()

# 初始化 OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

class LineWebhook(BaseModel):
    destination: str
    events: list

@app.post("/webhook")
async def webhook(req: Request):
    signature = req.headers["X-Line-Signature"]
    body = await req.body()
    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        return "Invalid signature", 400
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    # 根據使用者輸入判斷語氣（簡單示範：若輸入以 B: 開頭則使用選項 B）
    if user_message.startswith("B:"):
        role = "分析導向"
        user_message = user_message[2:].strip()
    else:
        role = "鏡像陪伴"

    messages = [
        {"role": "system", "content": get_prompt(role)},
        {"role": "user", "content": user_message}
    ]

    # 呼叫 OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7
    )

    reply_text = response.choices[0].message.content
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )