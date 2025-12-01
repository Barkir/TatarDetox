from datasets import load_dataset
import questionary
import os


def save_list(path, words):
    """Сохранить слова в файл"""
    with open(path, "w", encoding="utf-8") as f:
        for w in words:
            f.write(w + "\n")
    print(f"✔ Файл сохранён: {path}  (слов: {len(words)})")


def main():
    print("⏳ Загружаем датасет textdetox/multilingual_toxic_lexicon...")
    dataset = load_dataset("textdetox/multilingual_toxic_lexicon")

    # доступные языки (ключи словаря)
    languages = list(dataset.keys())

    lang = questionary.select(
        "Какой язык скачать?",
        choices=languages
    ).ask()

    print(f"📌 Выбран язык: {lang}")

    data = dataset[lang]

    # В датасете слова хранятся в колонке "text"
    words = list(set(data["text"]))  # уникальные

    os.makedirs("toxic_wordlists", exist_ok=True)
    output_path = f"toxic_wordlists/toxic_words_{lang}.txt"

    save_list(output_path, words)

    print("\n🎉 Готово!")
    print(f"Всего слов: {len(words)}")


if __name__ == "__main__":
    main()
