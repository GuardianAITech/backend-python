import json
import os
from openai import OpenAI
from helpers.data_converter import convert_to_dict
from helpers.etherscan_helpers import check_eth_contract_verification,get_ca_functions,get_ai_ca_transactions,get_internal_ai_ca_transactions
from helpers.filters import convert_booleans

from dotenv import load_dotenv
import re
load_dotenv()
openai_api_key = os.getenv("OPEN_AI_KEY")
client = OpenAI(api_key=openai_api_key)

def ai_analyze_contract(contract):
    with open('json/contracts.json', 'r') as json_file:
        weights = json.load(json_file)
    with open('json/contract_answers.json', 'r') as jsonx_file:
        answer = json.load(jsonx_file)
    cacode = check_eth_contract_verification(contract)
    
    if cacode != False:
        abi_list = json.loads(cacode.get('abi', []))
        abi_processed = [convert_booleans(entry) for entry in abi_list]
        function_names = get_ca_functions(abi_processed)
        source_code = cacode.get('sourcecode', '')
        catx = get_ai_ca_transactions(contract)
        caintx = get_internal_ai_ca_transactions(contract)

        prompt = (f"Given the Ethereum contract details and its functions listed below, "
              f"provide a detailed analysis in JSON format. The JSON should include "
              f"a 'functions' array with details about each function, and a 'summary' "
              f"object with the overall analysis text and a safety score. Use the following "
              f"structure for your response: {answer}. \n\n"
              f"Contract Source Code: {source_code}\n\n"
              f"Functions to analyze:\n")

    for function_name in function_names:
        prompt += f"- {function_name}\n"
    
    prompt += "\nInclude any relevant analysis based on the given transactions and internal transactions. and no less than 200 words:\n"
    prompt += f"Transactions: {catx}\nInternal Transactions: {caintx}\n"

   
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": "You are a developer analyzing Ethereum contracts."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7
        )
        response_text = chat_completion.choices[0].message.content
        print("Raw AI Response:", response_text)
        
        # Attempt to directly parse the AI response as JSON
        try:
            response_json = json.loads(response_text)
            print("Parsed JSON Response:", json.dumps(response_json, indent=4))
            return response_json
        except json.JSONDecodeError as e:
            print("Failed to parse AI response as JSON:", e)
            # Implement any fallback or post-processing here
    except Exception as e:
        print("An error occurred:", e)