import pandas as pd
import json
import numpy as np

def get_kengetallen_instruction(jaar_range, text_or_images):
    
    # Example dataframe for kengetallen
    columns = jaar_range
    index = [
        "netto schuldquote",
        "netto schuldquote, gecorrigeerd",
        "solvabiliteit",
        "grondexploitatie",
        "structurele exploitatieruimte",
        "belastingcapaciteit"
    ]

    # Generate random numbers between 0 and 1
    data = np.random.rand(len(index), len(columns))
    df = pd.DataFrame(data, index=index, columns=columns)
    df_json = df.to_json()
    example_json = json.dumps(df_json)
    
    # Instruction for the model
    text_instruction = f"""
    The text and tables you are given, contain data for six indicators, namely "netto schuldquote", 
    "netto schuldquote, gecorrigeerd", "solvabiliteit", "grondexploitatie", "structurele exploitatieruimte", 
    "belastingcapaciteit" for six years, {min(jaar_range)} to {max(jaar_range)}. Get the numbers for each 
    indicator and year and put them in a json array like {example_json}.

    These data may be displayed in several ways. Most often in a table with all the indicators and values. 
    Sometimes as text. Sometimes there are separate tables for each indicator, showing how they are calculated. 
    Ignore all other indicators which may be in the table. 

    Sometimes the indicators are called a bit differently than in the list above. For example, "netto schuldquote, 
    gecorrigeerd" may also be called "netto schuldquote, gecorrigeerd voor doorgeleende gelden". Or "belastingcapaciteit"
    may also be called "woonlasten".

    Sometimes there is also a table with all the indicators and values for "hoog", "middel" en "laag" "risico". 
    Ignore this table.

    Sometimes the values for some years are not filled in. Those can be set to null.
    
    If the values of the indicators cannot be obtained in the text and tables, return null on all values.

    Important:

    - Provide the JSON directly as an object, not as a text string (so no quotation marks around the whole thing, and 
    no escape characters like \n or \").
    - Do not add any extra explanation, comments, or markdown.
    - The response should be in a format that can be converted into a pandas dataframe through 
    pd.DataFrame.from_dict(data, orient='index')
    - If something cannot be determined, fill in null.
    """
    
    image_instruction = f"""
    The images you are given, contain data for six indicators, namely "netto schuldquote", 
    "netto schuldquote, gecorrigeerd", "solvabiliteit", "grondexploitatie", "structurele exploitatieruimte", 
    "belastingcapaciteit" for six years, {min(jaar_range)} to {max(jaar_range)}. Get the numbers for each 
    indicator and year and put them in a json array like {example_json}.

    These data may be displayed in one, several or all of the images shown, and in a number of different ways. 
    Most often in a table with all the indicators and values. Sometimes there are separate tables or graphs for each
    indicator, showing how they are calculated. Ignore all other indicators which may be in the tables or graphs. 

    Sometimes the indicators are called a bit differently than in the list above. For example, "netto schuldquote, 
    gecorrigeerd" may also be called "netto schuldquote, gecorrigeerd voor doorgeleende gelden". Or "belastingcapaciteit"
    may also be called "woonlasten".

    Sometimes there is also a table with all the indicators and values for "hoog", "middel" en "laag" "risico". 
    Ignore this table.

    Sometimes the values for some years are not filled in. Those can be set to null.
    
    If the values of the indicators cannot be obtained in the images, return null on all values.

    Important:

    - Provide the JSON directly as an object, not as a text string (so no quotation marks around the whole thing, and 
    no escape characters like \n or \").
    - Do not add any extra explanation, comments, or markdown.
    - The response should be in a format that can be converted into a pandas dataframe through 
    pd.DataFrame.from_dict(data, orient='index')
    - If something cannot be determined, fill in null.
    """
    
    if text_or_images == "text":
        return text_instruction
    elif text_or_images == "images":
        return image_instruction
    else:
        raise ValueError("text_or_images must be 'text' or 'images'")