import os
import httpx
import questionary
import pandas as pd
from dotenv import load_dotenv
import asyncio
from openai import OpenAI
import sys

load_dotenv()

OUTPUT_PATH = "Texts/output.tsv"

KEY_PROMPT =    "Ты — профессиональный лингвист, эксперт по татарскому языку, включая разговорный стиль, сленг, диалектные выражения и жаргон." \
                "Ты умеешь точно определять смысл, оттенки, эмоциональную окраску и прагматику фраз."                      \
                "Ты получаешь два текстовых фрагмента:" \
                "toxic_elem — оригинальная часть текста, содержащая токсичные слова и выражения."   \
                "non_toxic_elem — та же часть текста, но в ней токсичные слова просто удалены, из-за чего фраза стала неполной, нарушенной или потеряла свою выразительность."  \
                "Твоя задача:"  \
                "1. Проанализировать смысл исходного токсичного фрагмента (toxic_elem)."    \
                "2. Понять, какие элементы смысла были утрачены, когда токсичные слова были удалены (non_toxic_elem)."  \
                "3. Внутри non_toxic_elem — вставить отсутствующие слова или словосочетания, которые:"  \
                "- передают тот же смысл, что и токсичные элементы,"    \
                "- звучат натурально для татарской речи,"   \
                "- не являются токсичными," \
                "- не содержат оскорблений, мата, дегуманизации, агрессии." \
                "4. Сформировать гладкую, естественную, грамматически корректную татарскую фразу."  \
                "Принципы вставки слов:"    \
                "- Использовать эвфемизмы, мягкие аналоги, нейтральные выражения."  \
                "- Передавать тон и отношение, но без негативной агрессии." \
                "- Допускается лёгкая ирония, разговорность — если это улучшает естественность."    \
                "- Нельзя использовать прямые оскорбления или эмоционально резкие конструкции." \
                "Формат ответа .json с полями 'string_number', 'detoxified_text'(ОБЯЗАТЕЛЬНО СОБЛЮДАТЬ):"    \
                "НИЧЕГО, КРОМЕ ЭТОГО, СТРОГИЙ ФОРМАТ ОТВЕТА, ПО-ДРУГОМУ ПИСАТЬ НЕЛЬЗЯ!!!"


with open(OUTPUT_PATH, encoding="utf-8") as f:
    output_lines = [line.strip().split("\t") for line in f if line.strip()]

api_key = os.getenv("OPEN_ROUTER_API_KEY")
if not api_key:
    api_key = questionary.password("Enter your OpenRouter API key:").ask()
    if not api_key:
        raise ValueError("API key is required")

MODEL = ""
TIMEOUT = 60.0

def build_prompt(mat_slice) -> str:
    return  KEY_PROMPT + "\n" + "\n".join(mat_slice)


async def detoxify_sentence(mat_slice):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    prompt = build_prompt(mat_slice)
    print(prompt)
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash-preview-09-2025",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        extra_body={"reasoning": {"enabled": True}}
    )
    response = response.choices[0].message
    return response

async def main():
    if len(sys.argv) == 3:
        new_output_lines = []
        if int(sys.argv[2]) >= len(output_lines):
            new_output_lines = output_lines[int(sys.argv[1]):]
        else:
            new_output_lines = output_lines[int(sys.argv[1]):int(sys.argv[2])]


        results = []
        for i in range(0, len(new_output_lines), 10):
            print(f"\n[{i+1}/{len(new_output_lines)}] Обработка...")
            if (i+10 <= len(new_output_lines)):
                resulting = [",".join(k) for k in new_output_lines[i:i+10]]
                # print(resulting)
                result = await detoxify_sentence(resulting)
                results.append(result)
            else:
                resulting = [",".join(k) for k in new_output_lines[i:i+10]]
                # print(resulting)
                result = await detoxify_sentence(resulting)
                results.append(result)


    # Формируем таблицу
        df = pd.DataFrame(results)

    # Сохраняем в файл (можно .csv, но JSON сохраняет структуру ответа лучше)
        output_file = "output_results.json"
        df.to_json(output_file, orient="records", indent=2, force_ascii=False)
        print(f"\nРезультаты сохранены в {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
