from openai import OpenAI
from dotenv import load_dotenv
from flask import jsonify
import os
import json
import re
from helpers.data_converter import convert_to_dict
from datetime import datetime
load_dotenv()

openai_api_key = os.getenv("OPEN_AI_KEY")
client = OpenAI(api_key=openai_api_key)

def convert_datetime_to_string(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%dT%H:%M:%S")
    return obj

def check_wallet_with_ai(wallet_details):
    # Load weights
    with open('json/weights.json', 'r') as json_file:
        weights = json.load(json_file)

    with open('json/ai_wallet.json', 'r') as jsonx_file:
        answer = json.load(jsonx_file)

    # Convert datetime objects to strings
    for key, value in wallet_details.items():
        wallet_details[key] = convert_datetime_to_string(value)

    # Serialize wallet_details and weights
    weights_str = json.dumps(weights, indent=2)

    # Construct the prompt
    prompt = (
        "Analyze the following wallet details and calculate a safety score based on the given parameters and their weights. If parameters are missing, still keep calculating. Not all parameters have to be used.\n\n"
        f"Wallet Details: \n{wallet_details}\n\n"
        f"Security Parameters and Weights: \n{weights_str}\n\n"
        "The safety score is calculated as follows: Safety Score = (Parameter Score * Weight) / Total Weight.\n\n"
        "10 is the best safety score and 1 the worst.\n\n"
        "Write a comprehensive summary (150-250 words) about the wallet's security based on your knowledge about EVM wallets and the information you got from me. "
        "Always provide a safety score and a summary.\n\n"
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
        formatted_content = content.replace('\n', '')
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
        return {"error": str(e)}
