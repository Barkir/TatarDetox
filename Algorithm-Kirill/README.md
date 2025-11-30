# TATAR LANGUAGE DETOX RESEARCH
> AI ZAMAN HACKATHON TASK

![Python Badge](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff&style=for-the-badge)![Google Gemini Badge](https://img.shields.io/badge/Google%20Gemini-8E75B2?logo=googlegemini&logoColor=fff&style=for-the-badge)

**Overview**

- **Task**: Rewrite toxic text in the Tatar language by removing offensive language while preserving the original meaning.
- **Input**: Toxic sentences in Tatar (tt).
- **Output**: Detoxified version of the text in Tatar.

**Task Description**

Detecting toxicity in user-generated content is an important research area. Today, social media platforms attempt to address this issue, but most solutions rely on simply blocking undesirable messages. We propose a proactive approach: offering users a neutralized version of their message that retains its core intent. We refer to this process as **text detoxification**, which provides a constructive alternative to direct censorship.


|Input| Output|
|-----|-------|
|[toxic Tatar texts](./Texts/dev_inputs.tsv) | detoxified tatar text


### Approach #1
    accuracy = 0.27

- It was decided to use `bad words deletion` as the first approach

Used `gemini 2.5-flash` and creative prompt to get a database of [bad words](./old_scripts/combined.json).

Then we simply deleted these words from the original text.

### Approach #2
    accuracy = 0.47

- Then we decided to use `bad words dictionary` and prompt `gemini-flash 2.5` with both **toxic_text** and **toxic_text with deleted bad words**. This way we try to give llm more context, so it would detoxify the sentence. The code can be reviewed [here](./additional_context.py)

### Approach #3
    in progress

- The idea can be described in several steps.
1. Translate tatar text into english
2. detoxify english text using `baseline_mt0`
3. translate it back to tatar.

