from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
from pathlib import Path

from chatbot import extract_gender, extract_weather, build_reply
from recommender import OutfitRecommender
from rag import SimpleRAG


app = Flask(__name__)

DATASET_DIR = Path("dataset")

recommender = OutfitRecommender(DATASET_DIR)
rag = SimpleRAG("knowledge_base.txt")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dataset/<path:filename>")
def dataset_file(filename):
    return send_from_directory(DATASET_DIR, filename)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    user_message = data.get("message", "")

    gender = extract_gender(user_message)
    weather = extract_weather(user_message)

    recommendation = {
        "target_label": None,
        "items": {},
        "missing": []
    }

    image_urls = {}

    if gender is not None and weather is not None:
        recommendation = recommender.recommend(gender, weather)

        for item_name, image_path in recommendation["items"].items():
            relative_path = image_path.relative_to(DATASET_DIR)
            image_urls[item_name] = url_for(
                "dataset_file",
                filename=str(relative_path).replace("\\", "/")
            )

    rag_results = rag.search(user_message, top_k=2)
    rag_chunks = [item["chunk"] for item in rag_results]

    reply = build_reply(
        user_message=user_message,
        gender=gender,
        weather=weather,
        recommendation=recommendation,
        rag_chunks=rag_chunks
    )

    return jsonify({
        "reply": reply,
        "gender": gender,
        "weather": weather,
        "target_label": recommendation["target_label"],
        "images": image_urls
    })


if __name__ == "__main__":
    app.run(debug=True)