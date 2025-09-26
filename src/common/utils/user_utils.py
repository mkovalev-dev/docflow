import re


def initials_fi_no_dots(full_name: str) -> str:
    """
    Из полного ФИО возвращает две буквы: инициалы Фамилии и Имени (без точек).
    Примеры: 'Иванов Иван Петрович' -> 'ИИ', 'Петров-Сидоров Алексей' -> 'ПА'
    """
    # разбить по пробелам, убрать пустые куски
    parts = [p for p in re.split(r"\s+", full_name.strip()) if p]
    if not parts:
        return ""

    last = parts[0]
    first = parts[1] if len(parts) > 1 else ""

    # берём первую букву каждого (первая буквенная, с учётом дефисов и мусора)
    def first_alpha(s: str) -> str:
        for ch in s:
            if ch.isalpha():
                return ch
        return ""

    li = first_alpha(last.split("-")[0])
    fi = first_alpha(first)

    return (li + fi).upper()
