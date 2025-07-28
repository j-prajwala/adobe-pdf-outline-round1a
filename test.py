import os
import json
from src.extract_headings import extract_headings_from_pdf

def find_any_pdf(input_dir="input"):
    for file in os.listdir(input_dir):
        if file.lower().endswith(".pdf"):
            return os.path.join(input_dir, file)
    return None

def test_extraction_on_any_pdf():
    sample_path = find_any_pdf()
    
    if not sample_path or not os.path.exists(sample_path):
        print("❌ No PDF file found in the 'input/' directory. Please add at least one.")
        return

    print(f"✅ Running test on: {sample_path}")
    result = extract_headings_from_pdf(sample_path)

    # Basic structural checks
    assert isinstance(result, dict), "❌ Output is not a dictionary."
    assert "title" in result, "❌ Missing 'title' key."
    assert "outline" in result, "❌ Missing 'outline' key."
    assert isinstance(result["outline"], list), "❌ 'outline' is not a list."

    print("✅ Test passed.")
    print("Extracted title:", result["title"])

if __name__ == "__main__":
    test_extraction_on_any_pdf()
