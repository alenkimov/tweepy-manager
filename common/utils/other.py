def hidden_value(value: str) -> str:
    start = value[:3]
    end = value[-3:]
    return f"{start}**{end}"
