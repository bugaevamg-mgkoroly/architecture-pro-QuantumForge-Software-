import io
import os
import re
import sys
import time
import subprocess
from typing import Optional

from bs4 import BeautifulSoup

# ==========================================
# UTF-8
# ==========================================

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding="utf-8",
        errors="replace"
    )

# ==========================================
# НАСТРОЙКИ
# ==========================================

PAGES = {
    "Harry_Potter": "Harry_Potter.txt",
    "Hermione_Granger": "Hermione_Granger.txt",
    "Ron_Weasley": "Ron_Weasley.txt",
    "Luna_Lovegood": "Luna_Lovegood.txt",
    "Ginevra_Weasley": "Ginevra_Weasley.txt",
    "Neville_Longbottom": "Neville_Longbottom.txt",
    "Lord_Voldemort": "Lord_Voldemort.txt",
    "Draco_Malfoy": "Draco_Malfoy.txt",
    "Albus_Dumbledore": "Albus_Dumbledore.txt",
    "Severus_Snape": "Severus_Snape.txt",
    "Newt_Scamander": "Newt_Scamander.txt",
    "Tina_Goldstein": "Tina_Goldstein.txt",
    "Jacob_Kowalski": "Jacob_Kowalski.txt",
    "Queenie_Goldstein": "Queenie_Goldstein.txt",
    "Theseus_Scamander": "Theseus_Scamander.txt",
    "Gellert_Grindelwald": "Gellert_Grindelwald.txt",
    "Credence_Barebone": "Credence_Barebone.txt",
    "Aberforth_Dumbledore": "Aberforth_Dumbledore.txt",
    "Yusuf_Kama": "Yusuf_Kama.txt",
    "James_Potter_(I)": "James_Potter_(I).txt",
    "James_Potter_(II)": "James_Potter_(II).txt",
    "Arthur_Weasley": "Arthur_Weasley.txt",
    "Molly_Weasley": "Molly_Weasley.txt",
    "William_Weasley": "William_Weasley.txt",
    "Charles_Weasley": "Charles_Weasley.txt",
    "Percy_Weasley": "Percy_Weasley.txt",
    "Fred_Weasley": "Fred_Weasley.txt",
    "George_Weasley": "George_Weasley.txt",
    "Cho_Chang": "Cho_Chang.txt",
    "Dementor": "Dementor.txt",
    "Azkaban": "Azkaban.txt",
    "Hogwarts_School_of_Witchcraft_and_Wizardry": "Hogwarts_School_of_Witchcraft_and_Wizardry.txt",
    "Harry_Potter_and_the_Philosopher's_Stone": "Harry_Potter_and_the_Philosopher's_Stone.txt",
    "Harry_Potter_and_the_Chamber_of_Secrets": "Harry_Potter_and_the_Chamber_of_Secrets.txt",
    "Harry_Potter_and_the_Prisoner_of_Azkaban": "Harry_Potter_and_the_Prisoner_of_Azkaban.txt",
    "Harry_Potter_and_the_Goblet_of_Fire": "Harry_Potter_and_the_Goblet_of_Fire.txt",
}

BASE_URL = "https://harrypotter.fandom.com/wiki/"

ROOT_DIR = os.path.dirname(
    os.path.dirname(__file__)
)

OUTPUT_DIR = os.path.join(
    ROOT_DIR,
    "knowledge_base"
)

DEBUG_DIR = os.path.join(
    ROOT_DIR,
    "debug"
)

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================

def clean_text(text: str) -> str:

    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def save_debug_html(
    html: str,
    article_name: str
):

    os.makedirs(
        DEBUG_DIR,
        exist_ok=True
    )

    filepath = os.path.join(
        DEBUG_DIR,
        f"{article_name}.html"
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)

    return filepath


def save_debug_text(
    text: str,
    article_name: str
):

    filepath = os.path.join(
        DEBUG_DIR,
        f"{article_name}_text.txt"
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(text)

    return filepath


# ==========================================
# SAFARI
# ==========================================

def get_safari_html() -> str:

    script = """
    tell application "Safari"
        return source of front document
    end tell
    """

    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True
    )

    return result.stdout


def get_safari_title() -> str:

    script = """
    tell application "Safari"
        return name of front document
    end tell
    """

    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True
    )

    return result.stdout.strip()


# ==========================================
# ПРОВЕРКА CLOUDFLARE
# ==========================================

def is_cloudflare_html(
    html: str,
    title: str
) -> bool:

    title = title.lower()
    html_lower = html.lower()

    signatures = [
        "just a moment",
        "verify you are human",
        "challenge-platform",
        "cf-challenge",
        "cf-turnstile",
    ]

    if any(sig in title for sig in signatures):
        return True

    if any(sig in html_lower for sig in signatures):
        return True

    return False


# ==========================================
# ИЗВЛЕЧЕНИЕ ТЕКСТА
# ==========================================

def extract_article_text(
    html: str
) -> Optional[str]:

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    selectors = [
        ".mw-parser-output",
        "#mw-content-text",
        "main",
        "article",
        '[role="main"]',
        ".page-content",
        ".main-container",
    ]

    content = None

    for selector in selectors:

        found = soup.select_one(
            selector
        )

        if found:

            print(
                f"Найден контейнер: "
                f"{selector}"
            )

            content = found
            break

    if not content:

        print(
            "Контейнер статьи "
            "не найден."
        )

        body = soup.body

        if body:

            dump_path = os.path.join(
                DEBUG_DIR,
                "body_dump.html"
            )

            with open(
                dump_path,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(str(body))

            print(
                f"Body сохранён: "
                f"{dump_path}"
            )

        return None

    for tag in content.select(
        "script,"
        "style,"
        "table,"
        "nav,"
        "aside,"
        "figure,"
        "sup"
    ):
        tag.decompose()

    text = content.get_text(
        separator="\n"
    )

    lines = []

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            continue

        if line in {
            "[edit]",
            "[edit source]",
            "[]"
        }:
            continue

        lines.append(line)

    text = clean_text(
        "\n".join(lines)
    )

    return text


# ==========================================
# ЗАГРУЗКА СТАТЬИ
# ==========================================

def download_article(
    article_name: str
) -> Optional[str]:

    url = BASE_URL + article_name

    print(f"\nОткрываем Safari:")
    print(url)

    subprocess.run([
        "open",
        "-a",
        "Safari",
        url
    ])

    input(
        "\nПосле загрузки страницы "
        "нажмите Enter..."
    )

    html = get_safari_html()

    title = get_safari_title()

    print(f"\nTitle: {title}")
    print(
        f"Размер HTML: "
        f"{len(html):,} символов"
    )

    debug_file = save_debug_html(
        html,
        article_name
    )

    print(
        f"HTML сохранён: "
        f"{debug_file}"
    )

    if is_cloudflare_html(
        html,
        title
    ):

        print(
            "\nCloudflare всё ещё "
            "активен."
        )

        return None

    text = extract_article_text(
        html
    )

    if text:

        txt_file = save_debug_text(
            text,
            article_name
        )

        print(
            f"Текст сохранён: "
            f"{txt_file}"
        )

    return text


# ==========================================
# MAIN
# ==========================================

def main():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    os.makedirs(
        DEBUG_DIR,
        exist_ok=True
    )

    total = len(PAGES)

    success = 0
    failed = 0

    print(
        f"Начинаем загрузку "
        f"{total} страниц..."
    )

    for i, (
        article,
        filename
    ) in enumerate(
        PAGES.items(),
        start=1
    ):

        print(
            f"\n[{i}/{total}] "
            f"{article}"
        )

        filepath = os.path.join(
            OUTPUT_DIR,
            filename
        )

        text = download_article(
            article
        )

        if text:

            with open(
                filepath,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(text)

            print(
                f"\nСохранено:"
                f" {filepath}"
            )

            print(
                "\nПервые "
                "1000 символов:\n"
            )

            print(
                text[:1000]
            )

            success += 1

        else:

            print(
                "\nНе удалось "
                "получить статью."
            )

            failed += 1

        time.sleep(2)

    print("\n================")
    print(f"Успешно: {success}")
    print(f"Ошибок: {failed}")
    print("================")


if __name__ == "__main__":
    main()