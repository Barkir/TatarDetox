import csv
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parse_clean_text.py input.tsv", file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.is_file():
        print(f"File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Имя выходного файла
    output_path = input_path.with_name(input_path.stem + "_clean_id.tsv")

    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:

        reader = csv.DictReader(fin, delimiter="\t")

        # Заголовок
        fout.write("ID\ttat_toxic\ttat_detox1\n")

        next_id = 0   # ← начинаем с 0

        for row in reader:
            toxic = row.get("toxic_sentence", "").strip()
            neutral = row.get("neutral_sentence", "").strip()

            # Пропускаем строки без detox
            if not neutral:
                continue

            fout.write(f"{next_id}\t{toxic}\t{neutral}\n")
            next_id += 1

    print(f"✓ Файл сохранён: {output_path}")


if __name__ == "__main__":
    main()
