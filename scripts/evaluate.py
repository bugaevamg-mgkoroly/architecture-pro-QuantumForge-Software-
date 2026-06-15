"""
Задание 7: Автоматическое тестирование и аналитика RAG-бота.

Прогоняет золотой набор вопросов, оценивает качество ответов,
генерирует отчёт.
"""

import io
import json
import os
import sys
from datetime import datetime

# Принудительный UTF-8 для Windows-консоли
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from bot.rag_chain import ask

TESTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests")
GOLDEN_FILE = os.path.join(TESTS_DIR, "golden_questions.txt")


def load_golden_questions() -> list[dict]:
    """Загрузить золотой набор вопросов.

    Формат файла: каждые 2 строки — вопрос и ожидаемые ключевые слова.
    """
    questions = []
    with open(GOLDEN_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    for i in range(0, len(lines), 2):
        if i + 1 < len(lines):
            questions.append({
                "question": lines[i],
                "expected_keywords": [kw.strip() for kw in lines[i + 1].split(",")],
            })
    return questions


def evaluate_answer(answer: str, expected_keywords: list[str]) -> dict:
    """Оценить ответ по наличию ключевых слов."""
    answer_lower = answer.lower()
    found = [kw for kw in expected_keywords if kw.lower() in answer_lower]
    missing = [kw for kw in expected_keywords if kw.lower() not in answer_lower]

    score = len(found) / len(expected_keywords) if expected_keywords else 0
    return {
        "score": round(score, 2),
        "found_keywords": found,
        "missing_keywords": missing,
    }


def run_evaluation():
    """Прогнать все вопросы и сгенерировать отчёт."""
    print("=" * 60)
    print("  Автоматическое тестирование RAG-бота")
    print("=" * 60)

    questions = load_golden_questions()
    print(f"\nЗагружено {len(questions)} вопросов\n")

    results = []
    total_score = 0

    for i, q in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {q['question']}")

        result = ask(q["question"], interface="evaluate")
        eval_result = evaluate_answer(result["answer"], q["expected_keywords"])

        results.append({
            "question": q["question"],
            "answer": result["answer"],
            "status": result["status"],
            "score": eval_result["score"],
            "found_keywords": eval_result["found_keywords"],
            "missing_keywords": eval_result["missing_keywords"],
        })

        total_score += eval_result["score"]
        status_icon = "✓" if eval_result["score"] >= 0.5 else "✗"
        print(f"  {status_icon} Score: {eval_result['score']:.0%} "
              f"({len(eval_result['found_keywords'])}/{len(q['expected_keywords'])} keywords)")

        if eval_result["missing_keywords"]:
            print(f"    Missing: {', '.join(eval_result['missing_keywords'])}")

    # Общий отчёт
    avg_score = total_score / len(questions) if questions else 0
    passed = sum(1 for r in results if r["score"] >= 0.5)

    print("\n" + "=" * 60)
    print("  ОТЧЁТ")
    print("=" * 60)
    print(f"  Всего вопросов: {len(questions)}")
    print(f"  Пройдено (≥50%): {passed}/{len(questions)}")
    print(f"  Средний score: {avg_score:.0%}")
    print()

    # Анализ слабых мест
    weak = [r for r in results if r["score"] < 0.5]
    if weak:
        print("  Слабо покрытые темы:")
        for r in weak:
            print(f"    - {r['question']}")
            print(f"      Отсутствуют: {', '.join(r['missing_keywords'])}")
    else:
        print("  Все темы хорошо покрыты!")

    # Рекомендации
    print("\n  Рекомендации:")
    if weak:
        print("  1. Добавить документы по слабо покрытым темам")
        print("  2. Увеличить количество чанков (top-k) для улучшения контекста")
        print("  3. Проверить качество разбиения на чанки для проблемных документов")
    else:
        print("  1. Расширить золотой набор вопросов")
        print("  2. Добавить вопросы повышенной сложности (cross-document)")

    print("=" * 60)

    return results


def main():
    run_evaluation()


if __name__ == "__main__":
    main()