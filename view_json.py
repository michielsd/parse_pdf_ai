import streamlit as st
import pandas as pd
import json
import pdfplumber

PDF = "C:/Dashboard/Werk/llm_kengetallen/parse_pdf_ai/test_begrotingen/Beleidsbegroting 2025 - 2028 (definitief na raadsbesluit) kleinere pdf.pdf"
JSON = "C:/Dashboard/Werk/llm_kengetallen/parse_pdf_ai/jsons/b202.json"
PICKLE = "C:/Dashboard/Werk/llm_kengetallen/parse_pdf_ai/pickles/bele.pickle"

page_number = st.text_input("page number", value="1")

with pdfplumber.open(PDF) as pdf:
    page = pdf.pages[int(page_number) - 1]
    text = page.extract_text()
    images = page.images
    tables = page.extract_tables()

    page_content = {
        "text": text,
        "images": images,
        "tables": tables,
    }
    
    st.json(page_content)
    
with open(JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

#st.json(data)

#df = pd.read_pickle(PICKLE)

#st.write(df)
