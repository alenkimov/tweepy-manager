from pathlib import Path
from typing import Sequence, Generator


def read_fields_from_file(
        filepath: Path | str,
        *,
        separator: str = ":",
        fields: Sequence[str],
) -> Generator[dict, None, None]:
    """
    :param separator: Разделитель между данными в строке.
    :param fields: Кортеж, содержащий имена полей в порядке их появления в строке.
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            line.strip()
            if line == '\n':
                continue
            data = dict(zip(fields, line.split(separator)))
            data.update({key: None for key in data if not data[key]})
            yield data
