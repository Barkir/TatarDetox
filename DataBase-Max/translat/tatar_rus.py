import sys
from googletrans import Translator
import time

def main():
    translator = Translator()

    for line in sys.stdin:
        line = line.strip()

        # Пустые строки выводим как есть
        if not line:
            print("")
            continue

        # Переводим строку (с защитой от падений)
        try:
            result = translator.translate(line, dest="ru")
            print(result.text)
        except Exception as e:
            print(f"[ERROR] Не удалось перевести строку: {line}", file=sys.stderr)
            print("")
            time.sleep(0.5)

if __name__ == "__main__":
    main()
