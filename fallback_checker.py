def is_inappropriate(text):
    bad_words = ["幹", "媽的", "去死"]  # 可自行擴充
    return any(word in text.lower() for word in bad_words)