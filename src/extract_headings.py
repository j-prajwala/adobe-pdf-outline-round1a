import fitz  # PyMuPDF
import json
import os


def extract_headings_from_pdf(pdf_path):
    """
    Extract headings from PDF by analyzing font sizes, boldness,
    and additional style cues, then build hierarchical outline.
    """
    doc = fitz.open(pdf_path)
    font_sizes = []
    spans = []

    # Step 1: Extract and score all text spans
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        for b in blocks:
            if b['type'] != 0:
                continue  # Skip non-text blocks
            for line in b.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    if not text:
                        continue

                    size = span["size"]
                    font = span.get("font", "").lower()
                    flags = span.get("flags", 0)

                    is_bold = "bold" in font or flags & 2
                    is_caps = text.isupper() and len(text) >= 3

                    font_boost = 1.0
                    if is_bold:
                        font_boost += 0.2
                    if is_caps:
                        font_boost += 0.1
                    if "black" in font or "headline" in font:
                        font_boost += 0.2

                    weighted_size = size * font_boost
                    font_sizes.append(weighted_size)

                    spans.append({
                        "text": text,
                        "size": weighted_size,
                        "page": page_num + 1,
                        "font": font,
                        "is_bold": is_bold,
                    })

    # Step 2: Calculate thresholds for H1/H2/H3
    font_sizes = sorted(set(font_sizes), reverse=True)
    h1_size = font_sizes[0] if len(font_sizes) > 0 else 0
    h2_size = font_sizes[1] if len(font_sizes) > 1 else h1_size * 0.9
    h3_size = font_sizes[2] if len(font_sizes) > 2 else h2_size * 0.9

    print(f"[INFO] Font sizes (desc): {font_sizes}")
    print(f"[INFO] H1={h1_size}, H2={h2_size}, H3={h3_size}")

    # Step 3: Classify headings
    candidate_headings = []
    for span in spans:
        size = span["size"]
        text = span["text"]
        page = span["page"]
        is_bold = span["is_bold"]

        if len(text) < 3 or text.isnumeric():
            continue

        if abs(size - h1_size) < 0.5:
            level = "H1"
        elif abs(size - h2_size) < 0.5 and is_bold:
            level = "H2"
        elif abs(size - h3_size) < 0.5 and is_bold:
            level = "H3"
        else:
            continue

        candidate_headings.append({
            "level": level,
            "text": text,
            "page": page
        })

    # Step 4: Build hierarchical outline
    outline = build_hierarchy(candidate_headings)

    # Step 5: Title detection
    title_heading = next((h for h in candidate_headings if h["level"] == "H1"), None)
    title = title_heading["text"] if title_heading else os.path.basename(pdf_path)

    return {
        "title": title,
        "outline": outline
    }


def build_hierarchy(flat_headings):
    """
    Build hierarchical structure:
    - H2 under closest H1
    - H3 under closest H2
    """
    hierarchy = []
    current_h1 = None
    current_h2 = None

    for h in flat_headings:
        level = h["level"]
        h_entry = {
            "level": h["level"],
            "text": h["text"],
            "page": h["page"],
            "children": []
        }

        if level == "H1":
            hierarchy.append(h_entry)
            current_h1 = h_entry
            current_h2 = None
        elif level == "H2":
            if current_h1 is not None:
                current_h1["children"].append(h_entry)
            else:
                hierarchy.append(h_entry)
            current_h2 = h_entry
        elif level == "H3":
            if current_h2 is not None:
                current_h2["children"].append(h_entry)
            elif current_h1 is not None:
                current_h1["children"].append(h_entry)
            else:
                hierarchy.append(h_entry)

    return hierarchy


def process_all_pdfs(input_dir="input", output_dir="output"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(".pdf"):
            continue
        input_path = os.path.join(input_dir, filename)
        print(f"[INFO] Processing {input_path}...")
        outline_json = extract_headings_from_pdf(input_path)
        output_filename = filename[:-4] + ".json"
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(outline_json, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Saved outline JSON: {output_path}")


if __name__ == "__main__":
    process_all_pdfs()
