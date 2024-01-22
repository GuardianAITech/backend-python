import json
import os
from openai import OpenAI
from helpers.data_converter import convert_to_dict
from helpers.covalent_helpers import get_transaction_detailed
from dotenv import load_dotenv
import re
load_dotenv()
openai_api_key = os.getenv("OPEN_AI_KEY")
client = OpenAI(api_key=openai_api_key)
with open('json/weights.json', 'r') as json_file:
    weights = json.load(json_file)


def get_transaction_details(tx_hash):
    transaction = get_transaction_detailed(tx_hash)

    if transaction:
       return  split_transaction(transaction)
    else:
        return []
    
def split_transaction(transaction):
    details_keys = ["dex_details", "lending_details", "log_events", "safe_details"]
    
    general_transaction_data = {}

    for key, value in transaction.items():
        if key in details_keys and key == "dex_details":
            if value:
                transaction["is_dex_transaction"] = True
            else:
                transaction["is_dex_transaction"] = False
        elif key in details_keys and key == "lending_details":
            if value:
                transaction["is_lending_details"] = True
            else:
                transaction["is_lending_details"] = False
        elif key in details_keys and key == "safe_details":
            if value:
                transaction["is_safe_details"] = True
            else:
                transaction["is_safe_details"] = False

    check = analyze_with_gpt4(transaction)
    return check



    



def analyze_with_gpt4(transaction_json):
    with open('json/weights.json', 'r') as json_file:
        weights = json.load(json_file)
        weights_str = json.dumps(weights, indent=2)
    with open('json/ai_wallet.json', 'r') as jsonx_file:
        answer = json.load(jsonx_file)
        
    prompt = (
    "Analyze the following Ethereum transaction and calculate a safety score based on the given parameters and their weights. If parameters are missing, still keep calculating. Not all parameters have to be used. Mention some details if it's a DEX interaction, lending, or anything else.\n\n"
    f"Transaction: \n{transaction_json}\n\n"
    "Please create your summary text like this:\n"
    "Block Signed At: The transaction was included in a block on November 15, 2023.\n"
    "Block Height: The transaction was in block number 18575231.\n"
    "Successful: The transaction was successfully completed.\n"
    "From Address: The transaction was initiated from the address\n"
    "0x6f84e53b9c3749d5cb34cb0036f600ff0f9753a0\n"
    ".\n"
    "To Address: The transaction was sent to the address\n"
    "0x80a64c6d7f12c47b7c66c5b4e20e72bc1fcd5d9e\n"
    ".\n"
    "Value: The value of the transaction was\n"
    "0\n"
    "ETH, which means no ETH was transferred, suggesting it was a token transaction or a contract interaction.\n\n"
    
    "Gas Details:\n"
    "Gas Offered: The maximum amount of gas the sender was willing to use for the transaction was 312991 units.\n"
    "Gas Spent: The actual gas used was 156782 units.\n"
    "Gas Price: The price per unit of gas was 25518118077 wei.\n"
    "Fees Paid: The total fee for the transaction was\n"
    "4000781588348214\n"
    "wei (equivalent to {{4000781588348214/1000000000000000000}} ETH), or approximately $8.25 USD at the given rate.\n\n"
    
    "Dex Details:\n"
    "A swap event took place on the Uniswap protocol (version 2).\n"
    "From Token:\n"
    "ide.x.ai\n"
    "(ide) with a negative amount indicating tokens were sent by the transaction initiator.\n"
    "To Token: Wrapped Ether (WETH) with a positive amount indicating tokens were received by the transaction initiator.\n"
    "The swap was from approximately\n"
    "-1251111324161448\n"
    "ide tokens to\n"
    "62679701698626886 wei of WETH (equivalent to {{62679701698626886/1000000000000000000}} ETH).\n"
    "Value of Swap: The quoted USD value of the tokens swapped was roughly $124.33, indicating a likely swap of ide tokens for an equivalent value of WETH.\n\n"
    
    "Log Events:\n"
    "Multiple log events are associated with the transaction. These are likely events emitted by smart contracts during the transaction execution.\n"
    "The log events include interactions with the WETH token and the ide.x.ai token as part of the swap on Uniswap V2.\n\n"
    
    "The transaction seems to represent a token swap on Uniswap V2, a decentralized exchange, where the sender exchanged\n"
    "ide\ntokens for\n"
    "WETH\n"
    ". There were no Ether (ETH) transferred as part of the base transaction value, but gas fees were paid in ETH. The transaction was complex, involving several steps, as indicated by the number of log events."
    "Always provide a safety score and a summary. And make sure there is ALWAYS a safety score and a summary.\n\n"
    f"Security Parameters and Weights: \n{weights_str}\n\n"
    "The safety score is calculated as follows: Safety Score = (Parameter Score * Weight) / Total Weight.\n\n"
    "10 is the best safety score and 1 the worst.\n\n"
    "Format your response as a JSON object with a single 'summary' text and one 'safety_score'.\n\n"
    "Expected response format:\n"
    f"{answer}\n"
)


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
        if isinstance(formatted_content, str):
            try:
                response_dict = json.loads(formatted_content)
            except json.JSONDecodeError:
                        summary_match = re.search(r"'summary':\s*'((?:.*?)(?='safety_score'))", content, re.DOTALL)
                        score_match = re.search(r"'safety_score':\s*'([^']*)'", content)
                        summary = summary_match.group(1) if summary_match else 'No summary provided'
                        safety_score = score_match.group(1) if score_match else 'No safety score provided'
                        response_dict = {'summary': summary.strip(), 'safety_score': safety_score}
                        return response_dict
        elif isinstance(formatted_content, dict):
            response_dict = formatted_content
        else:
            return {"error": "Unexpected response format from AI"}

        # Extract summary and safety_score
        summary = response_dict.get('summary', 'No summary provided')
        safety_score = response_dict.get('safety_score', 'No safety score provided')

        # Construct a new dictionary with just summary and safety_score
        result = {
            'summary': summary,
            'safety_score': safety_score
        }

        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
