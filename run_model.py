from hashlib import md5
import os
import json
import base64
import dotenv
import numpy as np
from openai import OpenAI
import pandas as pd
import tiktoken
import re

from get_instruction import get_kengetallen_instruction, get_meerjarenraming_instruction, get_geprognosticeerde_balans_instruction, complete_json_instruction

# Globals
INPUT_FOLDER = "C:/Dashboard/Werk/llm_kengetallen/parse_pdf_ai/jsons/"
OUTPUT_FOLDER = "C:/Dashboard/Werk/llm_kengetallen/parse_pdf_ai/pickles/"

KG_JAAR_RANGE = range(2023, 2029) # WIJZIGEN VOOR JAAR BEGROTING. RANGE IS ZES JAAR: JR, LOPEND JAAR, BG, MJR, MJR+1, MJR+2, MJR+3
MJR_JAAR_RANGE = range(2025, 2029) # WIJZIGEN VOOR JAAR BEGROTING. RANGE IS VIER JAAR: BG, MJR, MJR+1, MJR+2, MJR+3
GPB_JAAR_RANGE = range(2023, 2029) # WIJZIGEN VOOR JAAR BEGROTING. RANGE IS VIER JAAR: BG, MJR, MJR+1, MJR+2, MJR+3

def main():
    # Load variables from .env file
    dotenv.load_dotenv()

    # Set client
    client = OpenAI()
    
    # Loop through JSONs
    for gm in os.listdir(INPUT_FOLDER):
        gm_key = gm[:-5]
        
        """
        if gm_key.startswith("kg_") and gm_key + ".pickle" not in os.listdir(OUTPUT_FOLDER):
            with open(INPUT_FOLDER + gm, "r", encoding="utf-8") as f:
                model_input = json.load(f)
            
            process_and_save(gm_key, OUTPUT_FOLDER, get_kengetallen(client, model_input, KG_JAAR_RANGE))
                            
        elif gm_key.startswith("mjr_"):
            with open(INPUT_FOLDER + gm, "r", encoding="utf-8") as f:
                model_input = json.load(f)
            
            process_and_save(gm_key, OUTPUT_FOLDER, get_meerjarenraming(client, model_input, MJR_JAAR_RANGE))
        
        """
        if gm_key.startswith("gpb_") and gm_key + ".pickle" not in os.listdir(OUTPUT_FOLDER):
            with open(INPUT_FOLDER + gm, "r", encoding="utf-8") as f:
                model_input = json.load(f)
            
            process_and_save(gm_key, OUTPUT_FOLDER, get_geprognosticeerde_balans(client, model_input, GPB_JAAR_RANGE))

def get_kengetallen(client, model_input, jaar_range):
    
    # Hard coded
    text_instruction = get_kengetallen_instruction(jaar_range, "text")
    image_instruction = get_kengetallen_instruction(jaar_range, "images")
    
    bg_content = model_input["bg_content"]
    bg_images = model_input["bg_images"]
    rp_content = model_input["rp_content"]
    rp_images = model_input["rp_images"]
    
    output = {}
    if bg_content:
        output = get_json_output(client, bg_content, "text", text_instruction)
    
    if not bg_content or is_empty(output):
        rp_chunks = chunk_text(rp_content, text_instruction)
        
        for chunk in rp_chunks:
            if not is_empty(output):
                break
            else:
                output = get_json_output(client, chunk, "text", text_instruction)
    
    if is_empty(output):
        output = get_json_output(client, rp_images, "images", image_instruction)

    df = pd.DataFrame.from_dict(output, orient='columns')
    return df

def get_meerjarenraming(client, model_input, jaar_range):
    
    # Hard coded
    text_instruction = get_meerjarenraming_instruction(jaar_range, "text")
    image_instruction = get_meerjarenraming_instruction(jaar_range, "images")
    
    rp_content = model_input["rp_content"]
    rp_images = model_input["rp_images"]
    
    output = {}
    rp_chunks = chunk_text(rp_content, text_instruction)
    for chunk in rp_chunks:
            if not is_empty(output):
                break
            else:
                output = get_json_output(client, chunk, "text", text_instruction)
    
    if is_empty(output):
        output = get_json_output(client, rp_images, "images", image_instruction)
        
    df = pd.DataFrame.from_dict(output, orient='columns')
    return df

def get_geprognosticeerde_balans(client, model_input, jaar_range):
    
    # Hard coded
    text_instruction = get_geprognosticeerde_balans_instruction(jaar_range, "text")
    image_instruction = get_geprognosticeerde_balans_instruction(jaar_range, "images")
    
    rp_content = model_input["rp_content"]
    rp_images = model_input["rp_images"]
    
    output = {}
    rp_chunks = chunk_text(rp_content, text_instruction)
    for chunk in rp_chunks:
            if not is_empty(output):
                break
            else:
                output = get_json_output(client, chunk, "text", text_instruction)
    
    if is_empty(output):
        output = get_json_output(client, rp_images, "images", image_instruction)
        
    flat = pd.json_normalize(output)
    
    tidy = []
    for col in flat.columns:
        parts = col.split(".")
        year = None
        for p in parts:
            if re.fullmatch(r"\d{4}", p):
                year = p
                break
            
        if year is None:
            # skip
            continue

         # category = everything except the year
        category_parts = [p for p in parts if p != year]
        category = " / ".join(category_parts)

        value = flat[col].iloc[0]
        tidy.append([category, year, value])
    
    df = pd.DataFrame(tidy, columns=["category", "year", "value"])
    
    result = df.pivot_table(index="category", columns="year", values="value")
    
    # Sort year columns numerically
    result = result.reindex(sorted(result.columns, key=int), axis=1)
    
    return result
    

def run_model(client, model_input, input_type, instruction):
    
    if input_type == "text":
        content = [{"type": "text", "text": instruction + "\n\n" + model_input}]
    elif input_type == "images":
        content = [{"type": "text", "text": instruction}]
        
        for image in model_input:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image}"}
            })
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ]
    )
    
    output = response.choices[0].message.content
    
    return output

def get_json_output(client, model_input, input_type, instruction):
    
    json_output = None
    
    model_output = run_model(client, model_input, input_type, instruction)
    
    if model_output.strip().endswith('}'):
        json_output = json.loads(model_output)
    else:
        complete_output = run_model(client, model_output, input_type, complete_json_instruction(model_output))
        json_output = json.loads(complete_output)
    
    print(json_output)
    
    return json_output

def is_empty(json_output):
    if isinstance(json_output, dict):
        df = pd.DataFrame.from_dict(json_output, orient='index')
        # Convert "None" strings → actual None
        df = df.replace("None", None)
        return True if (df.isnull()).all().all() else False

def chunk_text(text_input, instruction, model="gpt-4o"):
    MAX_TOKENS = 128000
    enc = tiktoken.encoding_for_model(model)
    
    text_tokens = enc.encode(text_input)
    instruction_tokens = enc.encode(instruction)    
    token_limit = MAX_TOKENS - len(instruction_tokens) - 500 # Safety margin
    
    chunks = []
    for i in range(0, len(text_tokens), token_limit):
        token_chunk = text_tokens[i:i + token_limit]
        text_chunk = enc.decode(token_chunk)
        chunks.append(text_chunk)
    
    return chunks

def process_and_save(gm_key, output_folder, function_result):
    if not is_empty(function_result):
        function_result.to_pickle(output_folder + f"{gm_key}.pickle")
        print(gm_key, function_result)
        print(f"[INFO] {gm_key} saved to pickle")
    else:
        print(f"[ERROR] {gm_key} not found")

if __name__ == "__main__":
    main()