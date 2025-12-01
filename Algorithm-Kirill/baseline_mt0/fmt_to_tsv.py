# code which parses
# toxic_sentence lang neutral_sentence to
# ID neutral_sentence

import csv

TSV_INPUT  = "baseline_output.tsv"
TSV_OUTPUT = "id_neutral.tsv"

with open(TSV_INPUT, 'w', encoding='utf-8', newline='') as f:
    rd =

with open(TSV_OUTPUT, "w", encoding="utf-8", newline='') as f:
    writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar='\\')
    writer.writerows(results)

