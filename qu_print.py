_text_value = ""


def get_text():
    return _text_value


def add(string: str):
    global _text_value
    _text_value += string + "\n"


def clear():
    global _text_value
    _text_value = ""
