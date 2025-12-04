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

def get_meerjarenraming_instruction(jaar_range, text_or_images):
    
    # Example dataframe for kengetallen
    columns = jaar_range
    index = [
        "totaal baten",
        "totaal lasten",
        "resultaat voor bestemming reserves",
        "incidentele baten",
        "incidentele lasten",
        "toevoegingen aan reserves",
        "onttrekkingen uit reserves",
        "resultaat na bestemming reserves",
    ]

    # Generate random numbers between 0 and 1
    data = np.random.rand(len(index), len(columns))
    df = pd.DataFrame(data, index=index, columns=columns)
    df_json = df.to_json()
    example_json = json.dumps(df_json)
    
    # Example for multi tiered table
    example_table_1 = """
    "08 Overige baten en lasten 9.446 46 944 3.293
    Lasten 11.472 1.632 3.429 5.779
    Baten 2.026 1.586 2.486 2.486
    11 Crisisbeheersing en Brandweer 24.828 25.725 26.899 28.085
    Lasten 24.828 25.725 26.899 28.085
    Baten 0 0 0 0
    """
    example_table_2 = """
    Begroting
    2023 2024 2025 2026 2027 2028
    Resultaat voor bestemming
    Baten
    1 Veiligheid 73 82 84 84 84 84
    2 Verkeer, vervoer en waterstaat 1.268 1.118 1.134 1.134 1.134 1.134
    Baten 376.976 417.912 422.902 395.045 383.946 389.115
    Lasten
    1 Veiligheid -9.595 -11.161 -11.438 -11.438 -11.377 -11.375
    2 Verkeer, vervoer en waterstaat -11.615 -12.284 -13.777 -13.635 -13.784 -14.350

    Lasten -357.760 -408.052 -415.800 -399.848 -386.032 -389.922
    Resultaat voor bestemming 19.216 9.859 7.103 -4.804 -2.085 -808
    Mutaties reserves
    Onttrekkingen aan reserves
    Onttrekkingen aan reserves 34.469 33.227 9.616 8.660 4.776 4.044
    Toevoegingen aan reserves
    Toevoegingen aan reserves -46.415 -42.941 -16.407 -4.647 -4.300 -4.079
    Mutaties reserves -11.946 -9.714 -6.791 4.014 476 -35
    Resultaat na bestemming 7.270 145 311 -790 -1.609 -843
    """
    
    text_instruction = f"""
    The text and tables you are given, contain a begroting or meerjarenraming for the years {min(jaar_range)} to 
    {max(jaar_range)}. Sometimes it contains more years. These are in the column headers of the table. The rows
    most often contain indicators like {', '.join(index)}. 
    
    There are multiple tables in the given text and tables that resemble the indicators and years in the list 
    above. Most of the time, these govern separate programs in the budget. The table you should return is the one
    that shows the sum of all programs. Get the rows and columns of this table and put them in a json array like 
    {example_json} and return it
    
    In the indicator names, replace spaces with underscores. So "totaal baten" becomes "totaal_baten".
    
    Note that the indicators may be called a bit differently than in the list above. For example, "totaal baten"
    may also be called "baten". Also, the baten and lasten may be split per program ("programma") or "taakveld".
    
    Often, the tables are multi tiered, with the first level being the program or taakveld, and the second level 
    being the indicator, like in {example_table_1}. Observe that it contains, for each taakveld and year, the
    baten, lasten and the balance ("saldo") between them. Return them separataly like follows, for example with the 
    taakveld "11 Crisisbeheersing en Brandweer", add them to rows in the output json array as 
    11_Crisisbeheersing_en_Brandweer_baten, 11_Crisisbeheersing_en_Brandweer_lasten and
    11_Crisisbeheersing_en_Brandweer_saldo.
    
    Sometimes, the taakvelden are placed under headers baten and lasten, like in {example_table_2}. In this case,
    return them separately like follows, for example with the taakveld "Veiligheid", add them to rows in the output
    json array as Veiligheid_baten and Veiligheid_lasten.
    
    Sometimes, the columns are subdivided into baten, lasten and balance ("saldo"). Here for each row, record values
    into rows as _baten, _lasten and _saldo.
    
    If there is nothing closely resembling the indicators and years in the list above, return a JSON with null on 
    all values.

    Important:

    - Provide the JSON directly as an object, not as a text string (so no quotation marks around the whole thing, and 
    no escape characters like \n or \").
    - Do not add any extra explanation, comments, or markdown.
    - The response should be in a format that can be converted into a pandas dataframe through 
    pd.DataFrame.from_dict(data, orient='index')
    - If something cannot be determined, fill in null.
    """
    
    image_instruction = f"""
    The images you are given, contain a begroting or meerjarenraming for the years {min(jaar_range)} to 
    {max(jaar_range)}. Sometimes it contains more years. These are in the column headers of the table. The rows
    most often contain indicators like {', '.join(index)}. 
    
    There are multiple tables in the given text and tables that resemble the indicators and years in the list 
    above. Most of the time, these govern separate programs in the budget. The table you should return is the one
    that shows the sum of all programs. Get the rows and columns of this table and put them in a json array like 
    {example_json} and return it
    
    In the indicator names, replace spaces with underscores. So "totaal baten" becomes "totaal_baten".
    
    Note that the indicators may be called a bit differently than in the list above. For example, "totaal baten"
    may also be called "baten". Also, the baten and lasten may be split per program ("programma") or "taakveld".
    
    Often, the tables are multi tiered, with the first level being the program or taakveld, and the second level 
    being the indicator, like in {example_table_1}. Observe that it contains, for each taakveld and year, the
    baten, lasten and the balance ("saldo") between them. Return them separataly like follows, for example with the 
    taakveld "11 Crisisbeheersing en Brandweer", add them to rows in the output json array as 
    11_Crisisbeheersing_en_Brandweer_baten, 11_Crisisbeheersing_en_Brandweer_lasten and
    11_Crisisbeheersing_en_Brandweer_saldo.
    
    Sometimes, the taakvelden are placed under headers baten and lasten, like in {example_table_2}. In this case,
    return them separately like follows, for example with the taakveld "Veiligheid", add them to rows in the output
    json array as Veiligheid_baten and Veiligheid_lasten.
    
    Sometimes, the columns are subdivided into baten, lasten and balance ("saldo"). Here for each row, record values
    into rows as _baten, _lasten and _saldo.
    
    If there is nothing closely resembling the indicators and years in the list above, return a JSON with null on 
    all values.

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

def complete_json_instruction(json_output):
    
    instruction = f"""
    The JSON you are given below, is not complete. 
    
    {json_output}
    
    Complete it using the information in the text and tables.
    
    Important:
    
    - Provide the JSON directly as an object, not as a text string (so no quotation marks around the whole thing, and 
    no escape characters like \n or \").
    - Do not add any extra explanation, comments, or markdown.
    - The response should be in a format that can be converted into a pandas dataframe through 
    pd.DataFrame.from_dict(data, orient='index')
    - If something cannot be determined, fill in null.
    """
    
    return instruction

def get_geprognosticeerde_balans_instruction(jaar_range, text_or_images):
    
    balans_positions = [
        "activa",
        "passiva",
        "eigen vermogen",
    ]
    
    text_instruction = f"""
    The text and tables you are given, contain a prognosticated balance sheet for the years {min(jaar_range)} to 
    {max(jaar_range)}. Sometimes it contains more years. These are in the column headers of the table. The rows
    contain indicators like {', '.join(balans_positions)}.
    
    Get the complete table, also the indicators that are not in the example table, and put them in a json array.
    
    Important:
    
    - Provide the JSON directly as an object, not as a text string (so no quotation marks around the whole thing, and 
    no escape characters like \n or \").
    - Do not add any extra explanation, comments, or markdown.
    - The response should be in a format that can be converted into a pandas dataframe through 
    pd.DataFrame.from_dict(data, orient='index')
    - If something cannot be determined, fill in null.
    """
    
    image_instruction = f"""
    The images you are given, contain a prognosticated balance sheet for the years {min(jaar_range)} to 
    {max(jaar_range)}. Sometimes it contains more years. These are in the column headers of the table. The rows
    contain indicators like {', '.join(balans_positions)}.
    
    Get the complete table, also the indicators that are not in the example table, and put them in a json array.
    
    Important:
    
    - Provide the JSON directly as an object, not as a text string (so no quotation marks around the whole thing, and 
    no escape characters like \n or \").
    - Do not add any extra explanation, comments, or markdown.
    - The response should be in a format that can be converted into a pandas dataframe through 
    pd.DataFrame.from_dict(data, orient='columns')
    - If something cannot be determined, fill in null.
    """
    
    if text_or_images == "text":
        return text_instruction
    elif text_or_images == "images":
        return image_instruction
    else:
        raise ValueError("text_or_images must be 'text' or 'images'")