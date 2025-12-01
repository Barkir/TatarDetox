import json
import sys
import argparse


def extract_toxic_words(model_output_json):
    toxic_list = []

    # Проходим по каждому ответу
    for idx, item in model_output_json["model_output"].items():

        # item — это строка с JSON, надо распарсить
        try:
            data = json.loads(item)
        except json.JSONDecodeError:
            continue

        words = data.get("toxic_words", [])

        for w in words:
            # Если хотя бы одно поле = True
            if (
                w.get("is_nationality_reference", False)
                or w.get("is_person_evaluation", False)
                or w.get("has_negative_emotion", False)
                or w.get("is_dehumanizing", False)
                or w.get("is_aggressive_or_imperative", False)
            ):
                toxic_list.append(w["word"])

    return toxic_list



def main():
    parser = argparse.ArgumentParser(description="Extract toxic words from model_output JSON")
    parser.add_argument("input_file", help="Path to JSON file with model_output")
    parser.add_argument("output_file", help="Where to save parsed toxic words")

    args = parser.parse_args()

    # Загружаем входной JSON
    with open(args.input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Извлекаем слова
    toxic_words = extract_toxic_words(data)

    # Удаляем дубликаты
    toxic_words = sorted(list(set(toxic_words)))

    # Формируем финальный JSON
    result = {"toxic_words": toxic_words}

    # Сохраняем
    with open(args.output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Готово! Сохранено в {args.output_file}")


if __name__ == "__main__":
    main()
