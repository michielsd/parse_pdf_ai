import os
import json
import base64
import dotenv
import numpy as np
from openai import OpenAI
import pandas as pd
import tiktoken

# DELETE GIT AND REDO WITH GITIGNORE

from get_instruction import get_kengetallen_instruction

# Globals
INPUT_FOLDER = "C:/Dashboard/Werk/llm_kengetallen/new_ed/jsons/"
OUTPUT_FOLDER = "C:/Dashboard/Werk/llm_kengetallen/new_ed/pickles/"

BEGROTING_JAAR = 2025 # JAAR BEGROTING
JAAR_RANGE = range(2023, 2029) # WIJZIGEN VOOR JAAR BEGROTING. RANGE IS ZES JAAR: JR, LOPEND JAAR, BG, MJR, MJR+1, MJR+2, MJR+3

def main():
    # Load variables from .env file
    dotenv.load_dotenv()

    # Set client
    client = OpenAI()
    
    # Loop through JSON
    for gm in os.listdir(INPUT_FOLDER):
        gm_code = gm[:4]
        if gm_code + ".pickle" not in os.listdir(OUTPUT_FOLDER):
            with open(INPUT_FOLDER + gm, "r", encoding="utf-8") as f:
                model_input = json.load(f)
            
            kengetallen = get_kengetallen(client, model_input, JAAR_RANGE)
            if not is_empty(kengetallen):
                kengetallen.to_pickle(OUTPUT_FOLDER + f"{gm_code}.pickle")
                print(gm_code, kengetallen)
                print(f"[INFO] kengetallen of {gm_code} saved to pickle")
            else:
                print(f"[ERROR] kengetallen of {gm_code} not found")

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
        output = run_model(client, bg_content, "text", text_instruction)
    
    if not bg_content or is_empty(output):
        rp_chunks = chunk_text(rp_content, text_instruction)
        
        for chunk in rp_chunks:
            if not is_empty(output):
                break
            else:
                output = run_model(client, chunk, "text", text_instruction)
    
    if is_empty(output):
        output = run_model(client, rp_images, "images", image_instruction)

    df = pd.DataFrame.from_dict(output, orient='columns')
    return df

def get_meerjarenraming(client, model_input, jaar_range):
    pass

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
    
    json_output = json.loads(response.choices[0].message.content)
    
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

if __name__ == "__main__":
    main()