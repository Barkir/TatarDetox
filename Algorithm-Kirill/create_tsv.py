import json
import csv
from similar_text import similar_text

TSV_ORIGINAL = "Texts/dev_inputs.tsv"
TOXIC_WORDS = "combined.json"
OUTPUT = "output.tsv"

def detoxify_message(msg: str, toxic_dict: str) -> str:
    for word in msg.split():
        for toxic_word in toxic_dict["toxic_words"]:
            if similar_text(word, toxic_word) >= 60:
                msg = msg.replace(word, "")
    return msg


with open(TOXIC_WORDS, "r") as file:
    data = json.load(file)

modified_rows = []
with open(TSV_ORIGINAL) as fd:
    rd = csv.reader(fd, delimiter="\t")
    iterator = 0
    for row in rd:
        msg = row[1]
        row.append(detoxify_message(msg, data))
        modified_rows.append(row)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(modified_rows)
