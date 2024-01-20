import json
import os
from openai import OpenAI
from helpers.data_converter import convert_to_dict
from helpers.covalent_helpers import get_transaction_detailed
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv("OPEN_AI_KEY")
client = OpenAI(api_key=openai_api_key)
with open('json/weights.json', 'r') as json_file:
    weights = json.load(json_file)


def get_transaction_details(tx_hash):
    transaction = get_transaction_detailed(tx_hash)

    if transaction:
       return  convert_to_dict(transaction["items"])
    else:
        return []
    
def split_transaction(transaction):
    details_keys = ["dex_details", "lending_details", "log_events", "safe_details"]
    
    general_transaction_data = {}

    for key, value in transaction.items():
        if key in details_keys:
            if value:
                if key == "dex_details":
                   dex = process_dex_details(value)
                elif key == "lending_details":
                   lending=  process_lending_details(value)
                elif key == "log_events":
                    events = process_log_events(value)
                elif key == "safe_details":
                    safedetails = process_safe_details(value)
        else:
            general_transaction_data[key] = value

    general = process_general_transaction_data(general_transaction_data)
    print(general)

def process_general_transaction_data(general_data):
    details = analyze_with_gpt4(general_data,"Analyze the following EVM transaction details and provide a summary:")
    return details

def process_dex_details(details):
    details = analyze_with_gpt4(details,"Analyze this Transaction Details of a Dex interaction and create a summary")
    return details

def process_lending_details(details):
    details = analyze_with_gpt4(details,"Analyze this Transaction Details of a Lending interaction and create a summary")
    return details

def process_log_events(events):
    events = analyze_with_gpt4(events,"Analyze this Transaction Details of Events and create a summary")
    return events

def process_safe_details(details):
    details = analyze_with_gpt4(details,"Analyze this Transaction Details of Safe details and create a summary")
    return details
    

def calculate_safety_score(transaction_details):
    total_weight = sum(weights.values())
    safety_score = sum(weights[param] * int(transaction_details.get(param, 0) != "") for param in weights) / total_weight

    return safety_score


def analyze_with_gpt4(transaction_json, addition):
    transaction_str = json.dumps(transaction_json) if isinstance(transaction_json, dict) else transaction_json
    
    prompt = f"{addition} {transaction_str}"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You are a developer.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            model="gpt-3.5-turbo-16k",
            temperature=0.7
        )
        content = chat_completion.choices[0].message.content
        print("API Response:", content)
        # response_object = json.loads(content)
        return content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
