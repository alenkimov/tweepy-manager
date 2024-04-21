import re
from typing import Iterable

import questionary


def _validate_float(value: str, min: float = None, max: float = None):
    try:
        float_val = float(value)
        if min is not None and float_val < min:
            return f"The value must be no less than {min}!"
        if max is not None and float_val > max:
            return f"The value must be no greater than {max}!"
        return True
    except ValueError:
        return "Please enter a valid floating-point number!"


def _validate_int(value: str, min: int = None, max: int = None):
    try:
        int_val = int(value)
        if min is not None and int_val < min:
            return f"The value must be no less than {min}!"
        if max is not None and int_val > max:
            return f"The value must be no greater than {max}!"
        return True
    except ValueError:
        return "Please enter a valid integer!"


INVALID_FILENAME_CHARS_RE = re.compile(r'[<>:"/\\|?*]')


def _validate_filename(value: str, blacklist: Iterable[str] = None):
    if not value:
        return "Filename cannot be empty!"

    if INVALID_FILENAME_CHARS_RE.search(value):
        return "Filename contains invalid characters!"

    if blacklist and value in blacklist:
        return f"Filename '{value}' is blacklisted!"

    return True


async def ask_float(message: str = "Enter value (float):", min: float = None, max: float = None) -> float:
    value = await questionary.text(message, validate=lambda text: _validate_float(text, min, max)).ask_async()
    return float(value)


async def ask_int(message: str = "Enter value (int):", min: int = None, max: int = None) -> int:
    value = await questionary.text(message, validate=lambda text: _validate_int(text, min, max)).ask_async()
    return int(value)


async def ask_filename(message: str = "Enter filename:", default: str = "", blacklist: Iterable[str] = None) -> str:
    filename = await questionary.text(
        message, default=default, validate=lambda text: _validate_filename(text, blacklist)).ask_async()
    return filename
