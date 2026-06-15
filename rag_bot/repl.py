"""Консольный REPL-интерфейс для RAG-бота."""

import sys
import io

# Принудительный UTF-8 для Windows-консоли
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

from bot.rag_chain import ask


def main():
    print("=" * 60)
    print("  QuantumForge Knowledge Base — REPL")
    print("  Введите вопрос или 'exit' для выхода")
    print("=" * 60)

    while True:
        try:
            query = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nДо свидания!")
            break

        if not query:
            continue
        if query.lower() in ("exit", "quit", "q", "выход"):
            print("До свидания!")
            break

        result = ask(query, interface="repl")

        print(f"\n{result['answer']}")

        if result["sources"]:
            print(f"\nИсточники: {', '.join(result['sources'])}")

        if result["status"] == "filtered":
            print("[!] Запрос был отфильтрован системой безопасности.")


if __name__ == "__main__":
    main()