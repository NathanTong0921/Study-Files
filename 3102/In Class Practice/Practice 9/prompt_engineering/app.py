import argparse
from collections import Counter
import tomllib
from pathlib import Path
import requests
import json

__all__ = ["get_chat_completion"]

# Load settings file
settings_path = Path("settings.toml")
with settings_path.open("rb") as settings_file:
    SETTINGS = tomllib.load(settings_file)

#load API key
def load_api_key(key_file):
    """Load API key from a local file."""
    with open(key_file, "r", encoding="utf-8") as f:
        return f.read().strip()
api_key = load_api_key("api_key.txt")

def parse_args() -> argparse.Namespace:
    """Parse command-line input."""
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=Path, help="Path to the input file")
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    file_content = args.file_path.read_text("utf-8")
    print(get_chat_completion(file_content))


def get_chat_completion(content: str) -> str:
    """Classify chats using self-consistency and majority voting."""
    url = "https://aigc-api.hkust-gz.edu.cn/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key
    }
    conversations = [chat for chat in content.split("\n\n") if chat.strip()]
    numbered_content = "\n\n".join(
        f"Conversation {index}:\n{chat}"
        for index, chat in enumerate(conversations, start=1)
    )
    samples = []

    for sample_number in range(SETTINGS["general"]["self_consistency_samples"]):
        data = {
            "model": SETTINGS["general"]["model"],
            "messages": _assemble_chat_messages(numbered_content),
            "temperature": SETTINGS["general"]["temperature"],
            "seed": 12345 + sample_number,
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        message = response.json()["choices"][0]["message"]["content"]
        samples.append(_parse_sentiments(message))

    expected_count = len(conversations)
    if any(len(sample) != expected_count for sample in samples):
        raise ValueError("The model did not return one sentiment per conversation")

    sentiments = [
        Counter(sample[index] for sample in samples).most_common(1)[0][0]
        for index in range(expected_count)
    ]
    return json.dumps({"sentiments": sentiments}, indent=2)


def _parse_sentiments(message: str) -> list[str]:
    """Extract and validate sentiment labels from a model response."""
    message = message.strip()
    if message.startswith("```"):
        message = message.split("\n", 1)[1].rsplit("```", 1)[0]

    sentiments = json.loads(message)["sentiments"]
    if any(sentiment not in {"negative", "positive"} for sentiment in sentiments):
        raise ValueError("The model returned an invalid sentiment label")
    return sentiments


def _assemble_chat_messages(content: str) -> list[dict]:
    """Combine all messages into a well-formatted list of dicts."""
    messages = [
        {"role": "system", "content": SETTINGS["prompts"]["role_prompt"]},
        {"role": "user", "content": SETTINGS["prompts"]["negative_example"]},
        {
            "role": "system",
            "content": SETTINGS["prompts"]["negative_reasoning"],
        },
        {
            "role": "assistant",
            "content": SETTINGS["prompts"]["negative_output"],
        },
        {"role": "user", "content": SETTINGS["prompts"]["positive_example"]},
        {
            "role": "system",
            "content": SETTINGS["prompts"]["positive_reasoning"],
        },
        {
            "role": "assistant",
            "content": SETTINGS["prompts"]["positive_output"],
        },
        {"role": "user", "content": f">>>>>\n{content}\n<<<<<"},
        {"role": "user", "content": SETTINGS["prompts"]["instruction_prompt"]},
    ]
    return messages


if __name__ == "__main__":
    main(parse_args())
