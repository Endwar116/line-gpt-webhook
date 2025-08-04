from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
from openai import OpenAI
import os
import uvicorn

app = FastAPI()

# 讀取環境變數
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

client = OpenAI(api_key=OPENAI_API_KEY)

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
def handle_message(user_id, user_input):
    # 儲存使用者訊息
    save_user_message(user_id, {"role": "user", "content": user_input})
    
    # 取得對話歷史（如需）
    history = get_user_history(user_id)
    
    # 建立完整 prompt（含語氣、記憶）
    messages = build_prompt(user_id, user_input, history)
    
    # 呼叫 GPT
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    reply_text = response['choices'][0]['message']['content']
    
    # fallback 檢查（語氣異常再修正）
    if is_robotic_response(reply_text):
        fallback_prompt = "請自然地、像人一樣溫柔地回答剛剛的問題，不要提到 AI 或系統。"
        messages = [{"role": "system", "content": fallback_prompt}, {"role": "user", "content": user_input}]
        response = openai.ChatCompletion.create(model="gpt-4", messages=messages)
        reply_text = response['choices'][0]['message']['content']

    return reply_text