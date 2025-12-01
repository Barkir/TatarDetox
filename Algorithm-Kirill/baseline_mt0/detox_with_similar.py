import json
import pandas as pd
import re
from difflib import SequenceMatcher
import sys

def load_toxic_words(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [word.strip().lower() for word in data.get("toxic_words", [])]

def normalize_word(word: str) -> str:
    # Убираем всё, кроме букв и апострофов, приводим к нижнему регистру
    return re.sub(r"[^а-яёa-z']+", "", word.lower())

def is_toxic_token(token: str, toxic_words: list, threshold: float = 0.8) -> bool:
    norm_token = normalize_word(token)
    if not norm_token:
        return False
    for tw in toxic_words:
        # Прямое совпадение — сразу токсично
        if norm_token == tw:
            return True
        # Проверяем сходство
        sim = SequenceMatcher(None, norm_token, tw).ratio()
        if sim >= threshold:
            return True
    return False

def detox_sentence(sentence: str, toxic_words: list, threshold: float = 0.8) -> str:
    if not isinstance(sentence, str):
        return ""
    # Разбиваем на токены, сохраняя разделители (чтобы можно было восстановить пробелы и пунктуацию)
    tokens = re.findall(r'\S+|\s+', sentence)
    cleaned_tokens = []
    for token in tokens:
        if token.isspace():
            cleaned_tokens.append(token)
        else:
            # Проверяем, является ли слово (без пунктуации) токсичным
            clean_word = re.sub(r'[^\w\']', '', token)
            if is_toxic_token(clean_word, toxic_words, threshold):
                # Пропускаем (удаляем)
                continue
            else:
                cleaned_tokens.append(token)
    # Собираем обратно и убираем лишние пробелы
    result = ''.join(cleaned_tokens)
    result = re.sub(r'\s+', ' ', result).strip()
    return result

def main(input_tsv: str, toxic_json: str, output_tsv: str):
    # Загружаем токсичные слова
    toxic_words = load_toxic_words(toxic_json)
    print(f"Loaded {len(toxic_words)} toxic words.")

    # Читаем TSV
    df = pd.read_csv(input_tsv, sep='\t', dtype=str)
    df = df.fillna('')

    output_rows = []
    for _, row in df.iterrows():
        toxic_elem = str(row.get('tat_toxic', ''))
        # Детоксифицируем
        non_toxic_elem = detox_sentence(toxic_elem, toxic_words, threshold=0.8)

        output_rows.append({
            'ID': row['ID'],
            'toxic_elem': toxic_elem,
            'non_toxic_elem': non_toxic_elem
        })

    # Сохраняем
    out_df = pd.DataFrame(output_rows)
    out_df.to_csv(output_tsv, sep='\t', index=False, quoting=3)  # quoting=3 = no quoting
    print(f"Saved {len(out_df)} rows to {output_tsv}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python detox_with_similar.py <input.tsv> <toxic_words.json> <output.tsv>")
        sys.exit(1)

    input_tsv = sys.argv[1]
    toxic_json = sys.argv[2]
    output_tsv = sys.argv[3]

    main(input_tsv, toxic_json, output_tsv)
