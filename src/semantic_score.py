import json
from sentence_transformers import SentenceTransformer, util
import os

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def score_headings(persona, headings):
    model = SentenceTransformer("all-MiniLM-L6-v2")

    persona_embedding = model.encode(persona, convert_to_tensor=True)

    for heading in headings:
        heading_embedding = model.encode(heading["text"], convert_to_tensor=True)
        score = util.cos_sim(persona_embedding, heading_embedding).item()
        heading["score"] = round(score * 100, 2)  # Convert to percentage

    return sorted(headings, key=lambda x: x["score"], reverse=True)

def main():
    input_json = "output/sample.json"
    persona_file = "persona.json"
    output_scored = "output/scored_output.json"

    if not os.path.exists(input_json) or not os.path.exists(persona_file):
        print("❌ Required files not found.")
        return

    headings = load_json(input_json)
    persona_data = load_json(persona_file)

    persona = persona_data.get("persona", "")
    if not persona:
        print("❌ Persona text missing.")
        return

    print("🧠 Scoring headings...")
    scored = score_headings(persona, headings)

    with open(output_scored, "w", encoding="utf-8") as f:
        json.dump(scored, f, indent=4, ensure_ascii=False)

    print(f"✅ Scored output saved to {output_scored}")

if __name__ == "__main__":
    main()
