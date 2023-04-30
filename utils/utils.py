def escape_markdownv2(text: str):
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    escaped_text = ''

    for char in text:
        if char in special_chars:
            escaped_text += '\\' + char
        else:
            escaped_text += char

    return escaped_text


def add_age_postfix(age):
    if age % 10 == 1 and age % 100 != 11:
        postfix = "год"
    elif age % 10 in [2, 3, 4] and age % 100 not in [12, 13, 14]:
        postfix = "года"
    else:
        postfix = "лет"

    return str(age) + " " + postfix
