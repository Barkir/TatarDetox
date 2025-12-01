import json
import csv
import re

TSV_ORIGINAL = "test_inputs.tsv"
JSON1 = "output.json"
OUTPUT = "output.tsv"

def detoxify_message(msg: str) -> str:
    if not msg.strip():
        return msg
    msg = msg.replace("```json", "").replace("```", "")
    return msg

detox_map = {}
results = []
with open(JSON1, "r", encoding="utf-8") as file:
    data = json.load(file)

for i in range(len(data)):
    msg = detoxify_message(" ".join(data[i]["0"][1:]))
    pattern = r'\{\s*"string_number"\s*:\s*(\d+)\s*,\s*"translated_text"\s*:\s*"((?:[^"\\]|\\.)*?)"\s*\}'
    for match in re.finditer(pattern, msg, re.DOTALL):
        string_number = int(match.group(1))
        escaped_text = match.group(2)
        try:
            translated_text = json.loads('"' + escaped_text + '"')
            results.append((string_number, translated_text))
        except json.JSONDecodeError:
            results.append((escaped_text.replace('\\"', '"')))


output_rows = []
with open(TSV_ORIGINAL, encoding="utf-8-sig") as fd:
    rd = csv.reader(fd, delimiter="\t")
    header = next(rd)
    output_rows.append(["ID", "tat_toxic", "tat_detox1"])

    line = 1
    for row in rd:
        if not row:
            continue
        id_val = row[0]
        tat_toxic = row[1] if len(row) > 1 else ""
        output_rows.append([int(id_val), tat_toxic])
    for i in range(len(results)):
        print(results[i])
        print(output_rows[i])
        if (results[i][0] == output_rows[i+1][0]):
            output_rows[i+1].append(results[i][1])

with open(OUTPUT, "w", encoding="utf-8", newline='') as f:
    writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar='\\')
    for row in output_rows:
        writer.writerow(row)

print(f"✅ {len(output_rows) - 1} rows processed. Saved to {OUTPUT}")
