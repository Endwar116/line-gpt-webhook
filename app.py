from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import os
import json
import uvicorn

# 匯入模組
from prompt_builder import build_prompt
from fallback_checker import is_robotic_response
from memory_json import save_user_message, get_user_history
import openai

# 初始化
app = FastAPI()

# 讀取環境變數（請在 Render 設定好）
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY

@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()

    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        return PlainTextResponse("Invalid signature", status_code=400)

    return PlainTextResponse("OK")

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_input = event.message.text

    # 儲存訊息
    save_user_message(user_id, {"role": "user", "content": user_input})

    # 抓取歷史訊息
    history = get_user_history(user_id)

    # 建立 prompt
    messages = build_prompt(user_id, user_input, history)

    # 呼叫 OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    reply_text = response['choices'][0]['message']['content']

    # 語氣 fallback 偵測
    if is_robotic_response(reply_text):
        fallback_prompt = "請自然地、像人一樣溫柔地回答剛剛的問題，不要提到 AI 或系統。"
        fallback_messages = [
            {"role": "system", "content": fallback_prompt},
            {"role": "user", "content": user_input}
        ]
        response = openai.ChatCompletion.create(model="gpt-4", messages=fallback_messages)
        reply_text = response['choices'][0]['message']['content']

    # 回傳
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )