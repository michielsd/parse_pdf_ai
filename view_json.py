import streamlit as st
import pandas as pd
import json

JSON = "C:/Dashboard/Werk/llm_kengetallen/new_ed/jsons/b202.json"
PICKLE = "C:/Dashboard/Werk/llm_kengetallen/new_ed/pickles/bele.json.pickle"

with open(JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.read_pickle(PICKLE)

st.write(df)
