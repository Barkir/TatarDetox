#!/usr/bin/env python3
import sys
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='auto', target='ru')

for line in sys.stdin:
    text = line.strip()
    if not text:
        print("")
        continue

    try:
        translated = translator.translate(text)
    except Exception as e:
        translated = f"[ERROR: {e}]"

    print(translated)
