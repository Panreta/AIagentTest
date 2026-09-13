import re
import json
import requests
import dotenv
import os


dotenv.load_dotenv()
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]


def compare_words(word1: str, word2: str) -> tuple:
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "openrouter/free",
            "temperature": 0,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Compare these two words/phrases:\n"
                        f"A: \"{word1}\"\n"
                        f"B: \"{word2}\"\n\n"
                        "How related or similar are they?\n"
                        "Respond with ONLY a JSON object, no other text, no markdown, "
                        "using double quotes for all keys and string values:\n"
                        '{"score": 0.0, "relationship": "short label", "reason": "one sentence"}'
                    ),
                }
            ],
        },
    )
    data = response.json()
    if "choices" not in data:
        raise RuntimeError(f"OpenRouter error: {data}")

    raw_text = data["choices"][0]["message"]["content"]

    match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    if not match:
        raise RuntimeError(f"No JSON object found in model output: {raw_text!r}")

    json_str = match.group(0)
    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse JSON: {json_str!r}") from e

    return parsed["score"], parsed["relationship"], parsed["reason"]


if __name__ == "__main__":
    score, relationship, reason = compare_words("WHOLEFDS MKT", "Whole Foods Market")
    print(f"score={score}, relationship={relationship}, reason={reason}\n")

    score, relationship, reason = compare_words("Starbucks", "Uber Eats")
    print(f"score={score}, relationship={relationship}, reason={reason}")