import os
import httpx
import asyncio
from dotenv import load_dotenv
from pathlib import Path

# Load ENV
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

INPUT_FILE = "test_inputs.tsv"
OUTPUT_FILE = "translated_en.tsv"

MODEL = "google/gemini-2.0-flash-001"
URL = "https://openrouter.ai/api/v1/chat/completions"

SLICE = 20  # batch size

PROMPT_HEADER = (
    "Translate the following Tatar sentences into English.\n"
    "Return ONLY raw translations, one per line, no JSON, no numbering.\n"
    "Meaning must be preserved.\n\n"
)

api_key = os.getenv("OPEN_ROUTER_API_KEY")
if not api_key:
    raise ValueError("OPEN_ROUTER_API_KEY missing!")


# Read input file (no tabs required)
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]


def build_prompt(batch):
    numbered = "\n".join(batch)
    return PROMPT_HEADER + numbered


async def translate_batch(batch):
    prompt = build_prompt(batch)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Title": "tt2en-nojson",
        "HTTP-Referer": "http://localhost"
    }

    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4000
    }

    async with httpx.AsyncClient(timeout=90) as client:
        r = await client.post(URL, headers=headers, json=body)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


async def main():
    out = open(OUTPUT_FILE, "w", encoding="utf-8")

    for i in range(0, len(lines), SLICE):
        batch = lines[i:i+SLICE]
        print(f"[{i}/{len(lines)}] Translating batch...")

        try:
            result = await translate_batch(batch)
        except Exception as e:
            print("❌ API ERROR:", e)
            continue

        translated_lines = [l.strip() for l in result.split("\n") if l.strip()]

        # If model returned fewer lines, pad with empty strings
        while len(translated_lines) < len(batch):
            translated_lines.append("")

        # Write TSV
        for idx, txt in enumerate(translated_lines):
            out.write(f"{i+idx}\t{txt}\ten\n")

    out.close()
    print("✔ DONE! Saved to", OUTPUT_FILE)


if __name__ == "__main__":
    asyncio.run(main())
