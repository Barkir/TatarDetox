#!/usr/bin/env python3
import csv
import json
import sys
from pathlib import Path
import requests

# -----------------------------------
#  НАСТРОЙКИ ДЛЯ OPENROUTER
# -----------------------------------

OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY"

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "openai/gpt-5"    # ← вызываем GPT-5

# -----------------------------------
#  СИСТЕМНЫЙ ПРОМПТ
# -----------------------------------

SYSTEM_PROMPT = """
Ты — профессиональный лингвист, эксперт по татарскому языку,
включая разговорный стиль, сленг и диалекты.

Ты получаешь два фрагмента:
- toxic_elem — оригинальный токсичный текст
- non_toxic_elem — версия текста, где токсичные слова удалены

Твоя задача — восстановить смысл, потерянный из-за удаления токсичных слов,
но вставить ТОЛЬКО мягкие, нетоксичные аналоги, которые:
- передают тот же смысл
- звучат естественно для татарского языка
- не содержат оскорблений, мата, агрессии, дегуманизации

Формат ответа:
[Преобразованный non_toxic_elem]
Только готовая переформулированная фраза без пояснений.
"""

# -----------------------------------
#  ФУНКЦИЯ: запрос к OpenRouter
# -----------------------------------

def call_openrouter(toxic_elem, non_toxic_elem):

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps({
                    "toxic_elem": toxic_elem,
                    "non_toxic_elem": non_toxic_elem
                }, ensure_ascii=False)
            }
        ],
        "temperature": 0.4
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    return data["choices"][0]["message"]["content"].strip()


# -----------------------------------
#  ОСНОВНОЙ КОД
# -----------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 detox_reconstruct_openrouter.py input.tsv", file=sys.stderr)
        sys.exit(1)

    input_file = Path(sys.argv[1])
    if not input_file.is_file():
        print(f"File not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    output_file = input_file.with_name(input_file.stem + "_detox.tsv")

    with open(input_file, "r", encoding="utf-8") as fin, \
         open(output_file, "w", encoding="utf-8", newline="") as fout:

        reader = csv.DictReader(fin, delimiter="\t")
        fieldnames = reader.fieldnames + ["detox_reconstructed"]
        writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()

        for row in reader:
            toxic_elem = row.get("tat_toxic", "")
            non_toxic_elem = row.get("tat_detox1", "")

            try:
                reconstructed = call_openrouter(toxic_elem, non_toxic_elem)
            except Exception as e:
                reconstructed = f"[ERROR: {e}]"

            row["detox_reconstructed"] = reconstructed
            writer.writerow(row)

    print(f"✓ Готово! Файл сохранён: {output_file}")


if __name__ == "__main__":
    main()
