import os
import httpx
import pandas as pd
from dotenv import load_dotenv
import asyncio
import json
import re

# ----------------------------
# Load environment
# ----------------------------
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(env_path)

api_key = os.getenv("OPEN_ROUTER_API_KEY")
if not api_key:
    raise ValueError("❌ OPEN_ROUTER_API_KEY not found in .env")

# ----------------------------
# Config
# ----------------------------
INPUT_PATH = "output_test_clean_only.txt"
OUTPUT_PATH = "translated_tatar.tsv"
PARTIAL_PATH = "translated_tatar_partial.tsv"

MODEL = "google/gemini-2.0-flash-001"
URL = "https://openrouter.ai/api/v1/chat/completions"

# ----------------------------
# Load input lines
# ----------------------------
with open(INPUT_PATH, encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

# Load partial progress
translated = {}
if os.path.exists(PARTIAL_PATH):
    df_prev = pd.read_csv(PARTIAL_PATH, sep="\t")
    for _, row in df_prev.iterrows():
        translated[int(row["ID"])] = row["tat_toxic"]


# ----------------------------
# JSON normalizer for Gemini
# ----------------------------
def normalize_json(raw: str):
    """Fix JSON returned by Gemini: remove markdown, wrap if needed, fix quotes."""

    if not raw or not raw.strip():
        return None

    text = raw.strip()

    # remove markdown fences
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)

    # remove zero-width chars
    text = "".join(c for c in text if ord(c) >= 32)

    # if it's a single object → wrap in array
    if text.startswith("{") and text.endswith("}"):
        text = "[" + text + "]"

    # remove trailing commas
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)

    # final cleanup
    try:
        parsed = json.loads(text)
        return parsed
    except Exception:
        # fallback: replace single quotes → double
        text2 = text.replace("'", '"')
        return json.loads(text2)


# ----------------------------
# Build prompt
# ----------------------------
PROMPT = """
Translate the following English sentence into Tatar.
Return STRICT JSON ONLY:
{
  "string_number": <ID>,
  "translated_text": "<translation>"
}
Sentence:
"""


# ----------------------------
# Call API
# ----------------------------
async def translate_one(idx: int, text: str):
    prompt = PROMPT + text

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost",
        "X-Title": "eng-to-tatar-translator",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(URL, headers=headers, json=payload)
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]

    # Normalize
    try:
        data = normalize_json(raw)
        return data[0]["translated_text"]
    except Exception:
        print("\n❌ Model returned invalid JSON:\n", raw)
        raise


# ----------------------------
# Main loop
# ----------------------------
async def main():
    for idx, text in enumerate(lines):

        # already translated?
        if idx in translated:
            print(f"[{idx}] SKIP")
            continue

        print(f"[{idx}] Translating...")

        # retry loop
        success = False
        for attempt in range(5):
            try:
                tt = await translate_one(idx, text)
                translated[idx] = tt
                success = True
                break
            except Exception:
                print(f"⚠ Retry {attempt+1}/5...")
                await asyncio.sleep(1)

        if not success:
            print(f"❌ Failed on line {idx}")
            translated[idx] = ""

        # autosave
        df_tmp = pd.DataFrame(
            [[i, translated[i], ""] for i in sorted(translated)],
            columns=["ID", "tat_toxic", "tat_detox1"],
        )
        df_tmp.to_csv(PARTIAL_PATH, sep="\t", index=False, encoding="utf-8")
        print("💾 Autosaved.")

    # Final save
    df = pd.DataFrame(
        [[i, translated[i], ""] for i in sorted(translated)],
        columns=["ID", "tat_toxic", "tat_detox1"],
    )
    df.to_csv(OUTPUT_PATH, sep="\t", index=False, encoding="utf-8")

    print(f"\n✔ DONE! Output saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
