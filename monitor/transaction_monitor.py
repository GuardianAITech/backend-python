import json
from dotenv import load_dotenv
from web3 import Web3
import os
from helpers.data_converter import convert_to_dict


with open('weights.json', 'r') as json_file:
    weights = json.load(json_file)

load_dotenv()

node = os.getenv("NODE_RPC")
web3 = Web3(Web3.HTTPProvider(node))
