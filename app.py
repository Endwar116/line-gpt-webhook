import os
import openai
from flask import Flask, request

app = Flask(__name__)  # ← ✅ Gunicorn 會找這個


@app.route("/webhook", methods=["POST"])
def webhook():
    from_line = request.get_json()
    print("收到 LINE 的請求內容：", from_line)  # 👈 幫助 debug

    if not from_line or "events" not in from_line or not from_line["events"]:
        print("⚠️ 無效的 events 或為空，跳過處理")
        return "Ignored empty events", 200  # ← LINE 不喜歡 500，要回 200 才不會被停權

    try:
        event = from_line["events"][0]

        if event["type"] != "message" or event["message"]["type"] != "text":
            return "Ignored non-text message", 200

        user_msg = event["message"]["text"]

        # GPT 回答邏輯
        openai.api_key = os.environ.get("OPENAI_API_KEY")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_msg}]
        )

        reply_msg = response["choices"][0]["message"]["content"]
        print("使用者說：", user_msg)
        print("GPT 回覆：", reply_msg)

        return "OK", 200

    except Exception as e:
        print("❌ 發生錯誤：", e)
        return "Internal Server Error", 500