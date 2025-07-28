import fitz  # PyMuPDF
import json
import os


def extract_headings_from_pdf(pdf_path):
    """
    Extract headings from PDF by analyzing font sizes and boldness,
    then build hierarchical outline.
    """
    doc = fitz.open(pdf_path)
    font_sizes = []
    text_blocks = []

    # Step 1: Extract all text spans info from all pages
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        for b in blocks:
            if b['type'] != 0:
                # Skip non-text blocks
                continue
            for line in b["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text:
                        continue
                    size = span["size"]
                    flags = span["flags"]
                    is_bold = bool(flags & 2)  # Bold check
                    # Store info
                    text_blocks.append({
                        "text": text,
                        "size": size,
                        "is_bold": is_bold,
                        "page": page_num + 1,
                        "font": span["font"],
                    })
                    font_sizes.append(size)

    # Step 2: Identify heading font-size thresholds (top 3 sizes)
    unique_sizes = sorted(set(font_sizes), reverse=True)
    h1_size = unique_sizes[0] if len(unique_sizes) > 0 else None
    h2_size = unique_sizes[1] if len(unique_sizes) > 1 else None
    h3_size = unique_sizes[2] if len(unique_sizes) > 2 else None

    # Debug print
    print(f"[INFO] Font sizes (desc): {unique_sizes}")
    print(f"[INFO] H1={h1_size}, H2={h2_size}, H3={h3_size}")

    # Step 3: Filter and classify headings using heuristic
    candidate_headings = []

    for block in text_blocks:
        size = block["size"]
        text = block["text"]
        page = block["page"]
        is_bold = block["is_bold"]

        # Ignore very short texts or numeric only
        if len(text) < 3 or text.isnumeric():
            continue

        # Heuristic for heading classification using size and boldness:
        if h1_size and abs(size - h1_size) < 0.5:
            level = "H1"
        elif h2_size and abs(size - h2_size) < 0.5 and is_bold:
            level = "H2"
        elif h3_size and abs(size - h3_size) < 0.5 and is_bold:
            level = "H3"
        else:
            continue

        candidate_headings.append({
            "level": level,
            "text": text,
            "page": page
        })

    # Step 4: Build hierarchy from flat heading list
    outline = build_hierarchy(candidate_headings)

    # Step 5: Determine title as first H1 or fallback to filename
    title_heading = next((h for h in candidate_headings if h["level"] == "H1"), None)
    title = title_heading["text"] if title_heading else os.path.basename(pdf_path)

    output = {
        "title": title,
        "outline": outline
    }

    return output


def build_hierarchy(flat_headings):
    """
    Build hierarchical outline as a nested list.
    H2 is child of closest preceding H1.
    H3 is child of closest preceding H2.
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
            if current_h1 is None:
                # No preceding H1, append at root
                hierarchy.append(h_entry)
            else:
                current_h1["children"].append(h_entry)
            current_h2 = h_entry
        elif level == "H3":
            if current_h2 is None:
                # No preceding H2, attach to last H1 if available
                if current_h1 is not None:
                    current_h1["children"].append(h_entry)
                else:
                    hierarchy.append(h_entry)
            else:
                current_h2["children"].append(h_entry)

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
