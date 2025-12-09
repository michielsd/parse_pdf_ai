import pdfplumber
import os
import json
import io
import base64
import pprint
from PIL import Image

PDF_FOLDER = "C:/Dashboard/Werk/llm_kengetallen/parse_pdf_ai/pdfs/"
OUTPUT_FOLDER = "C:/Dashboard/Werk/llm_kengetallen/parse_pdf_ai/jsons/"


def main():
    for pdf_name in os.listdir(PDF_FOLDER):
        info = analyze_pdf(os.path.join(PDF_FOLDER, pdf_name))

        if info["pdf_type"] == "Text-based PDF":

            kg = find_kengetallen(info["page_contents"])
            mjr = find_meerjarenraming(info["page_contents"])
            gpb = find_geprognosticeerde_balans(info["page_contents"])
            
            kg_pages = [p['page'] for p in kg['relevant_pages']]
            mjr_pages = [p['page'] for p in mjr['relevant_pages']]
            gpb_pages = [p['page'] for p in gpb['relevant_pages']]
            
            output = save_to_json(kg, "kg", pdf_name, OUTPUT_FOLDER)
            output = save_to_json(mjr, "mjr", pdf_name, OUTPUT_FOLDER)
            output = save_to_json(gpb, "gpb", pdf_name, OUTPUT_FOLDER)
            
            print(
                f"[INFO] kengetallen pages {kg_pages} of {pdf_name} saved to JSON"
            )
            print(
                f"[INFO] mjr pages {mjr_pages} of {pdf_name} saved to JSON"
            )
            print(
                f"[INFO] balans pages {gpb_pages} of {pdf_name} saved to JSON"
            )


def analyze_pdf(path):
    findings = {
        "num_pages": 0,
        "has_text": False,
        "text_on_most_pages": False,
        "has_images": False,
        "image_count": 0,
        "has_tables": False,
        "text_length": 0,
        "scan_like_pages": 0,
        "page_summaries": [],
        "page_contents": [],
    }

    with pdfplumber.open(path) as pdf:
        findings["num_pages"] = len(pdf.pages)

        for i, page in enumerate(pdf.pages, start=1):
            page_info = {
                "page": i,
                "text_present": False,
                "image_count": 0,
                "table_count": 0,
            }
            page_content = {
                "page": i,
                "text": None,
                "tables": None,
                "images": None,
            }

            # ---- 1. Detect real text ----
            text = page.extract_text()
            if text and text.strip():
                findings["has_text"] = True
                page_info["text_present"] = True
                findings["text_length"] += len(text.strip())
                page_content["text"] = text.strip()

            # ---- 2. Detect images ----
            images = page.images
            if images:
                findings["has_images"] = True
                page_info["image_count"] = len(images)
                page_content["images"] = images

            # ---- 3. Detect tables ----
            # pdfplumber's table extraction
            try:
                tables = page.extract_tables()
                if tables:
                    findings["has_tables"] = True
                    page_info["table_count"] = len(tables)
                    page_content["tables"] = tables
            except:
                pass

            # ---- 4. Is this a scan-like page? ----
            if page_info["image_count"] > 0 and not page_info["text_present"]:
                findings["scan_like_pages"] += 1

            findings["page_summaries"].append(page_info)
            findings["page_contents"].append(page_content)

    # ---- Summarize page summaries ----
    total_pages = len(findings["page_summaries"])
    if total_pages > 0:
        pages_with_text = sum(1 for summary in findings["page_summaries"]
                              if summary.get("text_present"))
        percent_with_text = (pages_with_text / total_pages) * 100
        findings["text_on_most_pages"] = percent_with_text >= 90

    del findings["page_summaries"]

    # ---- Final classification ----
    if findings["has_text"] and findings["text_on_most_pages"]:
        findings["pdf_type"] = "Text-based PDF"
    elif findings["has_images"]:
        findings["pdf_type"] = "Image-based scanned PDF"
    else:
        findings["pdf_type"] = "Unknown or empty PDF"

    return findings

def find_geprognosticeerde_balans(page_contents):
    
    keywords = [
        "geprognosticeerde balans",
        "balans",
        "vermogenspositie"
        "financiële positie"
        "meerjarenbalans",
        "activa",
        "passiva",
        "eigen vermogen",
    ]
    
    relevant_pages = []
    
    # Start at 2/3 of the way through the document
    length_of_page_contents = len(page_contents)
    start_page = int(2* (length_of_page_contents / 3))
    
    for page_content in page_contents:
        if page_content["text"] and page_content["page"] >= start_page:
         
            table_text = table_to_text(page_content["tables"])
            
            if any(k in page_content["text"] or k in table_text for k in keywords):
                relevant_pages.append(page_content["page"])
    
    relevant_pages_content = [
        page for page in page_contents if page["page"] in relevant_pages
    ]            
    
    return {
        "relevant_pages": relevant_pages_content,
    }

def find_meerjarenraming(page_contents):
    
    keywords = [
        "meerjarenraming",
        "meerjarenbegroting",
        "meerjarenbeeld",
        "begroting",
        "baten en lasten",
        "baten totaal",
        "lasten totaal",
        "totaal baten",
        "totaal lasten",
    ]
    
    relevant_pages = []
    
    # Start at 2/3 of the way through the document
    length_of_page_contents = len(page_contents)
    start_page = int(2* (length_of_page_contents / 3))
    
    for page_content in page_contents:
        if page_content["text"] and page_content["page"] >= start_page:
         
            table_text = table_to_text(page_content["tables"])
            
            if any(k in page_content["text"] or k in table_text for k in keywords):
                relevant_pages.append(page_content["page"])
    
    relevant_pages_content = [
        page for page in page_contents if page["page"] in relevant_pages
    ]            
    
    return {
        "relevant_pages": relevant_pages_content,
    }

def find_kengetallen(page_contents):
    title = "weerstandsvermogen en risicobeheersing"
    header = "kengetallen"
    kengetallen = [
        "schuldquote", "solvabiliteit", "grondexploitatie",
        "belastingcapaciteit", "exploitatieruimte"
    ]

    best_guess = None
    relevant_pages = {
        "title": None,
        "header": None,
        "schuldquote": None,
        "solvabiliteit": None,
        "grondexploitatie": None,
        "belastingcapaciteit": None,
        "exploitatieruimte": None,
    }

    for page_content in page_contents:
        if page_content["text"]:
            filled_count = sum(v is not None for v in relevant_pages.values())
            if filled_count >= 5:  # Can be altered
                continue
            
            table_text = table_to_text(page_content["tables"])
            
            if title in page_content["text"]:
                relevant_pages["title"] = page_content["page"]
            if header in page_content["text"]:
                relevant_pages["header"] = page_content["page"]
            if all(k in page_content["text"] or k in table_text for k in kengetallen):
                best_guess = page_content["page"]

            for kengetal in kengetallen:
                if kengetal in page_content["text"] or kengetal in table_text:
                    relevant_pages[kengetal] = page_content["page"]

    best_guess_content = next(
        (page for page in page_contents if page["page"] == best_guess), None)

    relevant_pages_numbers = set(v for v in relevant_pages.values()
                                 if v is not None)
    
    if len(relevant_pages_numbers) == 0:
        relevant_pages_numbers = [0, len(page_contents)]
    
    relevant_range = range(min(relevant_pages_numbers),
                           max(relevant_pages_numbers) + 10)  # Can be altered

    relevant_pages_content = [
        page for page in page_contents if page["page"] in relevant_range
    ]

    model_dicts = {
        "best_guess": best_guess_content,
        "relevant_pages": relevant_pages_content,
    }

    return model_dicts


def save_to_json(pages_of_interest, type_of_info, pdf_name, output_folder):

    bg_content = None
    bg_images = None
    if 'best_guess' in pages_of_interest and pages_of_interest["best_guess"]:
        bg_content = process_page(pages_of_interest["best_guess"])['content']
        bg_images = process_page(pages_of_interest["best_guess"])['images']

    pages_content = ""
    pages_images = []
    for page in pages_of_interest["relevant_pages"]:
        pages_content += "\n" + process_page(page)['content']
        for image in process_page(page)['images']:
            pages_images.append(image)

    model_data = {
        "bg_content": bg_content,
        "bg_images": bg_images,
        "rp_content": pages_content,
        "rp_images": pages_images,
    }

    model_data_json = json.dumps(model_data, ensure_ascii=False)
    # File names start with GM code
    output_name = type_of_info + "_" + pdf_name[:4]
    with open(os.path.join(output_folder, f"{output_name}.json"),
              "w",
              encoding="utf-8") as f:
        f.write(model_data_json)

    return model_data


def process_page(page):
    page_contents = {
        "page": page["page"],
        "content": None,
        "images": [],
    }

    text = page["text"]
    tables = page["tables"]
    combined_content = ""
    if text:
        combined_content += f"Tekst:\n{text}\n"
    if tables:
        for idx, table in enumerate(tables, start=1):
            combined_content += f"Tabel {idx}:\n{table}\n"
    # Store in content dict for downstream use
    page_contents["content"] = combined_content.strip()

    images = page["images"]
    if images:
        for i, img in enumerate(images, start=1):
            img_bytes = img["stream"].get_rawdata()
            try:
                pil_img = Image.open(io.BytesIO(img_bytes))
                # Convert to PNG (safe format)
                buffer = io.BytesIO()
                pil_img.save(buffer, format="PNG")
                img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                page_contents["images"].append(img_base64)
            except Exception:
                pass
            

    return page_contents

def table_to_text(tables):
    return " ".join(
        str(cell)
        for table in (tables or [])
        for row in table
        for cell in row
    )

# Example use:
if __name__ == "__main__":
    main()
