import chardet
import json

NUM_OF_LINES = 999999

def load_data_csv(file_path):
    """
    Load data from a CSV file, automatically detecting encoding.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        list: List of lists, where each sublist contains the values from a line in the CSV file.
    """
    raw = []
    data = []
    print("Loading data...")
    try:
        with open(file_path, 'rb') as file:
            result = chardet.detect(file.read())

        with open(file_path, 'r', encoding=result['encoding']) as file:
            for _ in range(NUM_OF_LINES):
                line = file.readline()
                if not line:  # Se chegou ao final do arquivo
                    break
                raw.append(line.replace("\n", ""))
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []
    
    
    for line in raw:
        # Split the line into a list of values
        values = line.split(',')
        # Append the list of values to the data list
        data.append(values)
    
    return data

def load_data_json(file_path):
    """
    Load data from a JSON file, automatically detecting encoding.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        list or dict: Parsed JSON data from the file.
    """
    json_file = []
    
    print("Loading data...")
    try:
        with open(file_path, 'rb') as file:
            result = chardet.detect(file.read())

        with open(file_path, 'r', encoding=result['encoding']) as file:
            json_file = json.load(file)
    
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []
    
    return json_file
