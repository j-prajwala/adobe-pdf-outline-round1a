import json
import os

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def flatten_outline(outline):
    flat = []

    def recurse(items):
        for item in items:
            flat.append((item["text"], item["level"], item["page"]))
            if item.get("children"):
                recurse(item["children"])
    recurse(outline)
    return flat

def precision_recall_f1(pred, gt):
    pred_set = set(pred)
    gt_set = set(gt)

    tp = len(pred_set & gt_set)
    fp = len(pred_set - gt_set)
    fn = len(gt_set - pred_set)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return precision, recall, f1

def evaluate_all(pred_dir="output", gt_dir="ground_truth"):
    scores = []
    files = sorted([f for f in os.listdir(pred_dir) if f.endswith(".json")])

    for fname in files:
        pred_path = os.path.join(pred_dir, fname)
        gt_path = os.path.join(gt_dir, fname)

        if not os.path.exists(gt_path):
            print(f"⚠️ Skipping {fname} (no ground truth)")
            continue

        pred = load_json(pred_path)
        gt = load_json(gt_path)

        pred_flat = flatten_outline(pred.get("outline", []))
        gt_flat = flatten_outline(gt.get("outline", []))

        precision, recall, f1 = precision_recall_f1(pred_flat, gt_flat)
        scores.append((precision, recall, f1))

        print(f"✅ {fname}: P={precision:.2f}, R={recall:.2f}, F1={f1:.2f}")

    if scores:
        avg_p = sum(s[0] for s in scores) / len(scores)
        avg_r = sum(s[1] for s in scores) / len(scores)
        avg_f1 = sum(s[2] for s in scores) / len(scores)
        print(f"\n📊 Average: P={avg_p:.2f}, R={avg_r:.2f}, F1={avg_f1:.2f}")
    else:
        print("⚠️ No matching files found for evaluation.")

if __name__ == "__main__":
    evaluate_all()
