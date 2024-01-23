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
    
    if(cacode != False):
         
         abi_list = json.loads(cacode.get('abi', []))
         abi_processed = [convert_booleans(entry) for entry in abi_list]
         function_names = get_ca_functions(abi_processed)
         source_code = cacode.get('sourcecode', '')
         catx = get_ai_ca_transactions(contract)
         caintx = get_internal_ai_ca_transactions(contract)

         
    prompt = (
     f"Please do a detailed analysis of the following functions using the source code provided below:\n\n"
    f"{source_code}\n\n"
    f"Comments in the source code can be fake, so ignore them and find out yourself what the function or variable is doing:\n\n"
    f"Also i am passing some last normal and internal transactions for even better security analysis:\n\n"
    f"{catx}\n\n"
    f"{caintx}\n\n"
    "Always provide a safety score and a summary. And make sure there is ALWAYS a safety score and a summary.\n\n"
    f"Security Parameters and Weights: \n{weights}\n\n"
    "The safety score is calculated as follows: Safety Score = (Parameter Score * Weight) / Total Weight.\n\n"
    "10 is the best safety score and 1 the worst.\n\n"
    "Format your response as a JSON object with a single 'summary' text and one 'safety_score'.\n\n"
    "Expected response format:\n"
    f"{answer}\n"
    "Here are the functions of the contract:"
)
    
    for function_name in function_names:
        prompt += f"- {function_name}\n"
    
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
        formatted_content = content
        print(formatted_content)

        return json.dumps(formatted_content)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    


