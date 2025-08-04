from flask import Flask, request
import os
from openai import OpenAI

client = OpenAI(
    api_key="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"
)

@app.route("/webhook", methods=["POST"])
def webhook():
    from_line = request.get_json()
    print("收到 LINE 的請求內容：", from_line)

    if not from_line or "events" not in from_line or not from_line["events"]:
        print("⚠️ 無效的 events 或為空，跳過處理")
        return "Ignored empty events", 200

    try:
        event = from_line["events"][0]
        if event["type"] != "message" or event["message"]["type"] != "text":
            return "Ignored non-text message", 200

        user_msg = event["message"]["text"]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_msg}]
        )

        reply_msg = response.choices[0].message.content
        print("使用者說：", user_msg)
        print("GPT 回覆：", reply_msg)

        return "OK", 200

    except Exception as e:
        print("❌ 發生錯誤：", e)
        return "Internal Server Error", 500