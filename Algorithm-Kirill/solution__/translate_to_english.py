import os
import httpx
import questionary
import pandas as pd
from dotenv import load_dotenv
import asyncio
from openai import OpenAI
import sys

load_dotenv()

SLICE=50
OUTPUT_PATH = "test_inputs.tsv"

KEY_PROMPT =    "Translate this tatar text to english\n" \
                "ANSWER FORMAT: .json with fields: 'string_number', 'translated_text' (The accuracy of filling in json is very important.)\n" \
                "NO ADDITIONAL TEXT OR DESCRIPTIONS. ONLY THIS TEXT"


with open(OUTPUT_PATH, encoding="utf-8") as f:
    output_lines = [line.strip().split("\t") for line in f if line.strip()][1:]

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
        model="meta-llama/llama-3.3-70b-instruct:free",
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
        for i in range(0, len(new_output_lines), SLICE):
            print(f"\n[{i+1}/{len(new_output_lines)}] Обработка...")
            if (i+SLICE <= len(new_output_lines)):
                resulting = [",".join(k) for k in new_output_lines[i:i+SLICE]]
                # print(resulting)
                result = await detoxify_sentence(resulting)
                results.append(result)
            else:
                resulting = [",".join(k) for k in new_output_lines[i:]]
                # print(resulting)
                result = await detoxify_sentence(resulting)
                results.append(result)


        df = pd.DataFrame(results)

        output_file = "output_results.json"
        df.to_json(output_file, orient="records", indent=2, force_ascii=False)
        print(f"\nРезультаты сохранены в {output_file}")

if __name__ == "__main__":
    asyncio.run(main())

