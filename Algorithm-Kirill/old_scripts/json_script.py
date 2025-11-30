#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def extract_toxic_words_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    toxic_words = set()

    # Обрабатываем как список сообщений (массив объектов)
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                # Ищем ключ "0", он содержит "content"
                if "0" in item:
                    content_field = item["0"]
                    if isinstance(content_field, list) and len(content_field) >= 2:
                        content_value = content_field[1]
                        if isinstance(content_value, str) and content_value.strip().startswith('{'):
                            try:
                                parsed = json.loads(content_value)
                                if "toxic_words" in parsed and isinstance(parsed["toxic_words"], list):
                                    toxic_words.update(parsed["toxic_words"])
                            except json.JSONDecodeError:
                                continue
    return toxic_words

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_toxic_words.py file1.json file2.json ...", file=sys.stderr)
        sys.exit(1)

    all_toxic_words = set()

    for filepath in sys.argv[1:]:
        if not Path(filepath).is_file():
            print(f"Warning: Skipping non-existent file: {filepath}", file=sys.stderr)
            continue
        try:
            words = extract_toxic_words_from_file(filepath)
            all_toxic_words.update(words)
        except Exception as e:
            print(f"Error processing {filepath}: {e}", file=sys.stderr)

    # Выводим в stdout в формате {"toxic_words": [...]}
    result = {"toxic_words": sorted(all_toxic_words)}
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
