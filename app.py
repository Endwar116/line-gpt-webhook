from flask import Flask, request, abort
import os
import openai

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    from_line = request.get_json()
    if not from_line:
        abort(400)
    user_msg = from_line["events"][0]["message"]["text"]

    # GPT 回答邏輯
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_msg}]
    )

    reply_msg = response["choices"][0]["message"]["content"]
    print("GPT 回覆：", reply_msg)
    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "LINE GPT Webhook is running."

if __name__ == "__main__":
    app.run(debug=True)
