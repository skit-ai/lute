def clip_to_len(text: str, maxlen: int, end="...") -> str:
    if len(text) <= maxlen:
        return text
    else:
        return text[:(maxlen - len(end))] + end
