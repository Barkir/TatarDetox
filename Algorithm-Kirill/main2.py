import os
import httpx
import questionary
import pandas as pd
from dotenv import load_dotenv
import asyncio
from openai import OpenAI

load_dotenv()

TATAR_PATH = "Texts/dev_inputs.tsv"
RUSSIAN_PATH = "Texts/dev_inputs_translated.tsv"

with open(TATAR_PATH, encoding="utf-8") as f:
    tatar_lines = [line.strip().replace("\t", " ") for line in f if line.strip()][450:]
    print(tatar_lines)

with open(RUSSIAN_PATH, encoding="utf-8") as f:
    russian_lines = [line.strip() for line in f if line.strip()][450:]

api_key = os.getenv("OPEN_ROUTER_API_KEY")
if not api_key:
    api_key = questionary.password("Enter your OpenRouter API key:").ask()
    if not api_key:
        raise ValueError("API key is required")

MODEL = "qwen/qwen3-embedding-8b"
TIMEOUT = 60.0

def build_prompt(tatar_sent: str, russian_sent: str) -> str:
    return (
        "Ты — детоксификатор предложений на татарском языке. "
        "Твоя задача — найти в предложении на татарском от 1 до 3 "
        "матерных или эмоционально окрашенных слов, делающих его токсичным.\n\n"
        f"Татарское предложение: {tatar_sent}\n"
        f"Русский перевод: {russian_sent}\n\n"
        "Ответь строго в формате JSON с полем 'toxic_words': список найденных слов (массив строк). "
        # "Если токсичных слов нет — верни пустой массив."
    )



async def detoxify_sentence(tatar_sent: str, russian_sent: str):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    response = client.chat.completions.create(
        model="x-ai/grok-4.1-fast",
        messages=[
            {
                "role": "user",
                "content": build_prompt(tatar_sent, russian_sent),
            }
        ],
        extra_body={"reasoning": {"enabled": False}}
    )
    response = response.choices[0].message
    return response

async def main():
    results = []
    for i, (tatar, russian) in enumerate(zip(tatar_lines, russian_lines)):
            print(f"\n[{i+1}/{len(tatar_lines)}] Обработка...")
            print(tatar, russian)
            result = await detoxify_sentence(tatar, russian)
            results.append(result)
            print(f"Татарский: {tatar}")
            print(f"Ответ модели:\n{result}\n")

    # Формируем таблицу
    df = pd.DataFrame(results)

    # Сохраняем в файл (можно .csv, но JSON сохраняет структуру ответа лучше)
    output_file = "detox_results2.json"
    df.to_json(output_file, orient="records", indent=2, force_ascii=False)
    print(f"\nРезультаты сохранены в {output_file}")

if __name__ == "__main__":
    asyncio.run(main())

