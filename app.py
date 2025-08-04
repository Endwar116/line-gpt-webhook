import os
from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import openai
import json

app = FastAPI()

# 讀取環境變數
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN or not OPENAI_API_KEY:
    raise ValueError("環境變數未設定正確")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY

# 模擬記憶儲存結構（僅記憶 10 則對話）
memory = {}

def save_user_message(user_id, message):
    if user_id not in memory:
        memory[user_id] = []
    memory[user_id].append(message)
    memory[user_id] = memory[user_id][-10:]  # 保留最近 10 則

def build_prompt(messages):
    system_prompt = {"role": "system", "content": "你是一個溫暖且能深入提問的情緒陪伴者。"}
    return [system_prompt] + messages

@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers["X-Line-Signature"]
    body = await request.body()

    try:
        events = parser.parse(body.decode(), signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            handle_message(event)

    return "OK"

def handle_message(event):
    user_id = event.source.user_id
    user_input = event.message.text

    # 儲存使用者輸入
    save_user_message(user_id, {"role": "user", "content": user_input})

    # 建立 prompt
    messages = build_prompt(memory[user_id])

    # 呼叫 GPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
    )
    reply_text = response.choices[0].message["content"]

    # 儲存 AI 回覆
    save_user_message(user_id, {"role": "assistant", "content": reply_text})

    # 回覆給 LINE 使用者
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )