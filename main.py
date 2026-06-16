#!/usr/bin/env python3

import json
import sys
import textwrap
import urllib.request
import urllib.error

API_KEY  = "PASTE_YOUR_API_HERE"
API_URL  = "https://openrouter.ai/api/v1/chat/completions"
MODEL    = "openai/gpt-oss-120b:free"
MAX_TOKENS = 3000

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BLUE   = "\033[94m"
MAGENTA= "\033[95m"
WHITE  = "\033[97m"


def c(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def rgb(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"


def rgb_banner():
    lines = [
        "   _____ __   _ ____   ______                __            ",
        "  / ___// /__(_) / /  / ____/_______  ____ _/ /_____  _____",
        r"  \__ \/ //_/ / / /  / /   / ___/ _ \/ __ `/ __/ __ \/ ___/",
        " ___/ / ,< / / / /  / /___/ /  / __/ /_/ / /_/ /_/ / /    ",
        r"/____/_/|_/_/_/_/   \____/_/   \___/\__,_/\__/\____/_/     ",
    ]
    stops = [(255,80,80), (255,200,50), (80,200,80), (50,150,255), (180,80,255)]
    for line in lines:
        total = len(line)
        for i, ch in enumerate(line):
            if ch == " ":
                print(" ", end="")
                continue
            t = i / max(total - 1, 1) * (len(stops) - 1)
            idx = int(t)
            frac = t - idx
            if idx >= len(stops) - 1:
                r, g, b = stops[-1]
            else:
                r = int(stops[idx][0] + (stops[idx+1][0] - stops[idx][0]) * frac)
                g = int(stops[idx][1] + (stops[idx+1][1] - stops[idx][1]) * frac)
                b = int(stops[idx][2] + (stops[idx+1][2] - stops[idx][2]) * frac)
            print(f"{rgb(r,g,b)}{ch}{RESET}", end="")
        print()


def banner():
    print()
    rgb_banner()
    print()


def section(title: str):
    print()
    print(c(f"\u25b8 {title}", YELLOW + BOLD))
    print(c("\u2500" * 52, DIM))


def ask(prompt: str, default: str = "") -> str:
    hint = f" {c(f'[{default}]', DIM)}" if default else ""
    raw = input(f"  {c('?', GREEN + BOLD)} {prompt}{hint}: ").strip()
    return raw if raw else default


def ask_multi(prompt: str, hint: str = "через запятую") -> list[str]:
    raw = input(f"  {c('?', GREEN + BOLD)} {prompt} {c(f'({hint})', DIM)}: ").strip()
    return [x.strip() for x in raw.split(",") if x.strip()]


def spinner_print(msg: str):
    frames = ["\u280b", "\u2819", "\u2839", "\u2838", "\u283c", "\u2834", "\u2826", "\u2827", "\u2807", "\u280f"]
    import time, threading

    stop = threading.Event()

    def spin():
        i = 0
        while not stop.is_set():
            sys.stdout.write(f"\r  {c(frames[i % len(frames)], CYAN)}  {msg}  ")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

    t = threading.Thread(target=spin, daemon=True)
    t.start()
    return stop


def preview(content: str):
    print()
    print(c("\u2554" + "\u2550" * 52 + "\u2557", MAGENTA))
    print(c("\u2551  PREVIEW SKILL.md" + " " * 35 + "\u2551", MAGENTA + BOLD))
    print(c("\u2560" + "\u2550" * 52 + "\u2563", MAGENTA))
    for line in content.splitlines():
        wrapped = textwrap.wrap(line, width=50) if line else [""]
        for wl in wrapped:
            print(c("\u2551 ", MAGENTA) + f"{wl:<50}" + c("  \u2551", MAGENTA))
    print(c("\u255a" + "\u2550" * 52 + "\u255d", MAGENTA))


def call_api(messages: list[dict]) -> str:
    payload = json.dumps({
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": messages,
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "HTTP-Referer": "https://github.com/Artyom151/skill-creator",
            "X-Title": "skill-creator",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {body}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Сетевая ошибка: {e.reason}")


SYSTEM_PROMPT = (
    "Ты — эксперт по созданию SKILL.md файлов для ИИ-агентов (например Claude).\n"
    "SKILL.md — это инструкция для ИИ, которая описывает, как именно выполнять конкретный навык (skill).\n"
    "\n"
    "Структура SKILL.md должна содержать:\n"
    "1. YAML-заголовок (---) с полями: name, description, version, author (если указано)\n"
    "2. # Название навыка\n"
    "3. Краткое описание (1-2 предложения)\n"
    "4. ## Когда использовать этот навык\n"
    "5. ## Пошаговый процесс (нумерованный список с конкретными действиями)\n"
    "6. ## Важные правила и ограничения\n"
    "7. ## Примеры использования (если тема предполагает)\n"
    "8. ## Советы по качеству\n"
    "\n"
    "Пиши чётко, конкретно и практично. Инструкции должны быть настолько ясными,\n"
    "что ИИ сможет точно воспроизвести нужное поведение.\n"
    "Язык документа определяется пожеланием пользователя (русский или английский)."
)


def build_user_prompt(info: dict) -> str:
    parts = [
        f"Тема / название навыка: {info['topic']}",
        f"Описание задачи: {info['description']}",
        f"Целевой ИИ-агент: {info['agent']}",
        f"Язык документа: {info['language']}",
    ]
    if info.get("style"):
        parts.append(f"Стиль изложения: {', '.join(info['style'])}")
    if info.get("palette"):
        parts.append(f"Цветовая палитра / визуальный стиль: {', '.join(info['palette'])}")
    if info.get("rules"):
        parts.append(f"Особые правила: {', '.join(info['rules'])}")
    if info.get("examples"):
        parts.append(f"Примеры использования: {', '.join(info['examples'])}")
    if info.get("author"):
        parts.append(f"Автор: {info['author']}")
    if info.get("version"):
        parts.append(f"Версия: {info['version']}")
    if info.get("extra"):
        parts.append(f"Дополнительно: {info['extra']}")

    parts.append("\nСгенерируй полный SKILL.md файл на основе этих данных.")
    return "\n".join(parts)


def collect_info() -> dict:
    section("Основная информация")
    topic       = ask("Тема / название навыка")
    while not topic:
        print(c("  ✗ Тема обязательна!", RED))
        topic = ask("Тема / название навыка")

    description = ask("Опишите задачу (что должен делать ИИ с этим навыком)")
    agent       = ask("Для какого ИИ-агента", "Claude")
    language    = ask("Язык документа (русский / english)", "русский")

    section("Стиль и оформление")
    style   = ask_multi("Стиль изложения (например: строгий, дружелюбный, технический, краткий)")
    palette = ask_multi("Цветовая палитра или визуальные предпочтения")

    section("Правила и примеры")
    rules    = ask_multi("Особые правила или ограничения для этого навыка")
    examples = ask_multi("Примеры использования (кратко)")

    section("Мета-информация")
    author  = ask("Автор (необязательно)")
    version = ask("Версия", "1.0.0")
    extra   = ask("Любые дополнительные пожелания (необязательно)")

    return {
        "topic": topic,
        "description": description,
        "agent": agent,
        "language": language,
        "style": style,
        "palette": palette,
        "rules": rules,
        "examples": examples,
        "author": author,
        "version": version,
        "extra": extra,
    }


def save_file(content: str, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(c(f"\n  ✓ Сохранено: {filename}", GREEN + BOLD))


def main():
    banner()

    if API_KEY == "PASTE_YOUR_API_HERE":
        print(c("  ✗ Установите API-ключ OpenRouter в переменной API_KEY!", RED + BOLD))
        print(c("    Получить: https://openrouter.ai/keys", DIM))
        sys.exit(1)

    info = collect_info()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": build_user_prompt(info)},
    ]

    print()
    stop = spinner_print("Генерирую скилл…")
    try:
        result = call_api(messages)
    except RuntimeError as e:
        stop.set()
        sys.stdout.write("\r" + " " * 60 + "\r")
        print(c(f"\n  ✗ Ошибка API: {e}", RED))
        sys.exit(1)
    finally:
        stop.set()

    sys.stdout.write("\r" + " " * 60 + "\r")
    print(c("  ✓ Готово!", GREEN + BOLD))

    while True:
        preview(result)

        print()
        print(c("  Что дальше?", BOLD))
        print(f"  {c('1', CYAN)} — Сохранить файл")
        print(f"  {c('2', CYAN)} — Внести правки / доработки")
        print(f"  {c('3', CYAN)} — Сгенерировать заново")
        print(f"  {c('4', CYAN)} — Выйти без сохранения")
        choice = input(f"\n  {c('→', YELLOW)} Выберите (1-4): ").strip()

        if choice == "1":
            save_file(result, "SKILL.md")
            break

        elif choice == "2":
            edit_req = ask("Опишите, что изменить или добавить")
            if not edit_req:
                continue
            messages.append({"role": "assistant", "content": result})
            messages.append({"role": "user",      "content": edit_req})

            stop2 = spinner_print("Обновляю SKILL.md…")
            try:
                result = call_api(messages)
            except RuntimeError as e:
                stop2.set()
                sys.stdout.write("\r" + " " * 60 + "\r")
                print(c(f"\n  ✗ Ошибка: {e}", RED))
                continue
            finally:
                stop2.set()

            sys.stdout.write("\r" + " " * 60 + "\r")
            print(c("  ✓ Обновлено!", GREEN + BOLD))

        elif choice == "3":
            stop3 = spinner_print("Генерирую заново…")
            messages_fresh = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": build_user_prompt(info)},
            ]
            try:
                result = call_api(messages_fresh)
                messages = messages_fresh
            except RuntimeError as e:
                stop3.set()
                sys.stdout.write("\r" + " " * 60 + "\r")
                print(c(f"\n  ✗ Ошибка: {e}", RED))
                continue
            finally:
                stop3.set()

            sys.stdout.write("\r" + " " * 60 + "\r")
            print(c("  ✓ Готово!", GREEN + BOLD))

        elif choice == "4":
            print(c("\n  До свидания!", CYAN))
            break
        else:
            print(c("  Введите 1, 2, 3 или 4", RED))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(c("\n\n  Прерван пользователем.", CYAN))
        sys.exit(0)
