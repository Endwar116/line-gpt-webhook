def build_prompt(history):
    # 開頭系統角色設定
    prompt = [{"role": "system", "content": "你是一個溫柔而專業的 AI 助手，善於用清楚、友善的語氣與使用者對話。"}]
    prompt.extend(history[-10:])  # 取最近十則對話記錄
    return prompt