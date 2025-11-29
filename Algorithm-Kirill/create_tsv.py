import json
import csv
from similar_text import similar_text

TSV_ORIGINAL = "Texts/dev_inputs.tsv"
TOXIC_WORDS = "combined.json"
OUTPUT = "output.tsv"


def detoxify_message(msg: str, toxic_dict: dict) -> str:
    if not msg.strip():  # если сообщение пустое — вернуть как есть
        return msg

    words = msg.split()
    cleaned_words = []
    for word in words:
        replaced = False
        for toxic_word in toxic_dict["toxic_words"]:
            if similar_text(word, toxic_word) >= 60:
                # пропускаем токсичное слово (заменяем на пустую строку)
                replaced = True
                break
        if not replaced:
            cleaned_words.append(word)

    result = " ".join(cleaned_words)
    # Если результат пуст — вернуть исходное сообщение
    return result if result.strip() else msg


# Загрузка токсичных слов
with open(TOXIC_WORDS, "r", encoding="utf-8") as file:
    data = json.load(file)

modified_rows = []

with open(TSV_ORIGINAL, encoding="utf-8-sig") as fd:
    rd = csv.reader(fd, delimiter="\t")
    header = next(rd)  # читаем заголовок
    print(header)
    # Ожидаем: ['ID', 'tat_toxic']
    # assert len(header) == 2 and header[0] == "ID" and header[1] == "tat_toxic", \
        # "Unexpected header in input TSV"

    # Добавляем третий столбец
    new_header = ["ID", "tat_toxic", "tat_detox1"]
    modified_rows.append(new_header)

    for row in rd:
        row_id = row[0]
        msg = row[1]

        detox_msg = detoxify_message(msg, data)

        # Гарантируем, что нет пустого значения
        if not detox_msg.strip():
            detox_msg = msg

        modified_rows.append([row_id, msg, detox_msg])

# Запись результата
with open(OUTPUT, "w", encoding="utf-8", newline='') as f:
    writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar='\\')
    writer.writerows(modified_rows)

print(f"✅ {len(modified_rows) - 1} rows processed. Saved to {OUTPUT}")
