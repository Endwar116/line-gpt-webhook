from flask import Flask, request, abort
import os
import openai

app = Flask(__name__)

# 對接路由，這裡非常重要要是 /callback
@app.route("/webhook", methods=["POST"])
def webhook():
    from_line = request.get_json()

    if not from_line or "events" not in from_line:
        abort(400)

    try:
        user_msg = from_line["events"][0]["message"]["text"]
    except KeyError:
        return "Ignored (not a text message)", 200  # LINE 有可能發 sticker、follow event

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


@app.route("/", methods=["GET"])
def healthcheck():
    return "LINE GPT Webhook is running.", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)