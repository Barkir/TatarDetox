import re
import json
import csv

TSV_OUTPUT = "baseline.tsv"
with open("output_results.json", "r") as f:
    data = json.load(f)

header = ["toxic_sentence", "lang"]
lang = "en"

results = []
results.append(header)

for i in range(len(data)):
    content = data[i]["0"][1]
    pattern = r'\{\s*"string_number"\s*:\s*(\d+)\s*,\s*"translated_text"\s*:\s*"((?:[^"\\]|\\.)*?)"\s*\}'
    for match in re.finditer(pattern, content, re.DOTALL):
        string_number = int(match.group(1))
    # Декодируем escape-последовательности вручную (например, \", \\, \n)
        escaped_text = match.group(2)
    # Оборачиваем в кавычки и парсим как JSON-строку
        try:
            translated_text = json.loads('"' + escaped_text + '"')
            results.append((translated_text, lang))
        except json.JSONDecodeError:
        # Если не получилось — пропускаем или оставляем как есть
            results.append((escaped_text.replace('\\"', '"'), lang))

# Вывод
# for num, text in results:
    # print(f"[{num}] {text}")


with open(TSV_OUTPUT, "w", encoding="utf-8", newline='') as f:
    writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar='\\')
    writer.writerows(results)

