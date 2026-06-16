from pathlib import Path
import re
import random


def normalize_text(text):
    return text.lower().strip()


def load_response_rules(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        return []

    rules = []

    lines = file_path.read_text(encoding="utf-8").splitlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        if "=>" not in line:
            continue

        key, replies_text = line.split("=>", 1)

        key = normalize_text(key)

        replies = replies_text.split("||")
        replies = [reply.strip() for reply in replies if reply.strip()]

        if key and replies:
            rules.append((key, replies))

    return rules


def phrase_matches(message, phrase):
    pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
    return re.search(pattern, message) is not None


def get_basic_reply(user_message):
    message = normalize_text(user_message)

    small_talk_rules = load_response_rules("small_talk.txt")

    # Check longer phrases first.
    # Example: "what can you do" should be checked before "hi".
    small_talk_rules.sort(key=lambda item: len(item[0]), reverse=True)

    for phrase, replies in small_talk_rules:
        if phrase_matches(message, phrase):
            return random.choice(replies)

    return None


def get_outfit_reply(gender, weather):
    target_label = f"{gender}_{weather}"

    outfit_rules = load_response_rules("outfit_replies.txt")

    matching_replies = []

    for key, replies in outfit_rules:
        if key == target_label:
            matching_replies.extend(replies)

    if matching_replies:
        return random.choice(matching_replies)

    return "Here is a suitable outfit recommendation based on your gender and the weather."


def extract_gender(user_message):
    message = user_message.lower()

    male_words = ["male", "man", "boy", "guy", "nam"]
    female_words = ["female", "woman", "girl", "lady", "nữ", "nu"]

    for word in female_words:
        if word in message:
            return "female"

    for word in male_words:
        if word in message:
            return "male"

    return None


def extract_weather(user_message):
    message = user_message.lower()

    hot_words = [
    "hot",
    "warm",
    "sunny",
    "summer",
    "humid",
    "heat",
    "heated",
    "boiling",
    "scorching",
    "sweaty",
    "sunshine",
    "high temperature",
    "very hot",
    "too hot",

    # Vietnamese without accents
    "nong",
    "troi nong",
    "mua he",
    "oi buc",
    "nang",
    "troi nang",

    # Vietnamese with accents
    "nóng",
    "trời nóng",
    "mùa hè",
    "oi bức",
    "nắng",
    "trời nắng"
]
    cold_words = [
    "cold",
    "cool",
    "chilly",
    "freezing",
    "winter",
    "snowy",
    "snow",
    "frosty",
    "windy",
    "low temperature",
    "very cold",
    "too cold",

    # Vietnamese without accents
    "lanh",
    "troi lanh",
    "mua dong",
    "ret",
    "gio lanh",
    "se lanh",

    # Vietnamese with accents
    "lạnh",
    "trời lạnh",
    "mùa đông",
    "rét",
    "gió lạnh",
    "se lạnh"
]

    for word in hot_words:
        if word in message:
            return "hot"

    for word in cold_words:
        if word in message:
            return "cold"

    return None


def build_reply(user_message, gender, weather, recommendation, rag_chunks):
    basic_reply = get_basic_reply(user_message)

    if basic_reply is not None:
        return basic_reply

    if gender is None and weather is None:
        return (
            "Please tell me your gender and the weather. "
            "For example: 'I am male and it is hot today.'"
        )

    if gender is None:
        return "Please tell me your gender: male or female."

    if weather is None:
        return "Please tell me the weather: hot or cold."

    missing = recommendation["missing"]

    if missing:
        missing_text = ", ".join(missing)
        return (
            f"I can suggest an outfit for {gender} users in {weather} weather, "
            f"but I could not find these items in the dataset: {missing_text}."
        )

    return get_outfit_reply(gender, weather)