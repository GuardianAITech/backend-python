import json
from helpers.data_converter import convert_to_dict
from helpers.covalent_helpers import get_transaction_detailed

with open('json/weights.json', 'r') as json_file:
    weights = json.load(json_file)


def get_transaction_details(tx_hash):
    transaction = get_transaction_detailed(tx_hash)

    if transaction:
       return  convert_to_dict(transaction["items"])
    else:
        return []

def calculate_safety_score(transaction_details):
    total_weight = sum(weights.values())
    safety_score = sum(weights[param] * int(transaction_details.get(param, 0) != "") for param in weights) / total_weight

    return safety_score