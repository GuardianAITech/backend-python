from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timedelta

load_dotenv()
etherscan_api_key = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_API_BASE = "https://api.etherscan.io/api"
ANALYZE_DAYS = os.getenv("ANALYZE_DAYS")

def get_internal_transactions(wallet_address, start_block, end_block, page=1):
    params = {
        "module": "account",
        "action": "txlistinternal",
        "address": wallet_address,
        "startblock": start_block,
        "endblock": end_block,
        "page": page,
        "offset": 10,
        "sort": "desc",
        "apikey": etherscan_api_key,
    }

    response = requests.get(ETHERSCAN_API_BASE, params=params)
    result = response.json()
    
    if result["status"] == "1":
        return result["result"]
    else:
        return []
    
def get_normal_transactions(wallet_address, start_block, end_block, page=1):
    params = {
        "module": "account",
        "action": "txlist",
        "address": wallet_address,
        "startblock": start_block,
        "endblock": end_block,
        "page": page,
        "offset": 10,
        "sort": "desc",
        "apikey": etherscan_api_key,
    }

    response = requests.get(ETHERSCAN_API_BASE, params=params)
    result = response.json()
    
    if result["status"] == "1":
        return result["result"]
    else:
        return []
    
def get_current_block():
    params = {
        "module": "proxy",
        "action": "eth_blockNumber",
        "apikey": etherscan_api_key,
    }

    response = requests.get(ETHERSCAN_API_BASE, params=params)
    result = response.json()

    if "result" in result:
        return int(result["result"], 16)
    else:
        return None
    

def get_block_number_3_months_ago():
    three_months_ago = datetime.now() - timedelta(days=int(ANALYZE_DAYS))
    timestamp_three_months_ago = int(three_months_ago.timestamp())
    block_number = get_block_number_by_timestamp(timestamp_three_months_ago)
    return block_number

def get_block_number_by_timestamp(timestamp):
    params = {
        "module": "block",
        "action": "getblocknobytime",
        "timestamp": timestamp,
        "closest": "before",
        "apikey": etherscan_api_key,
    }

    response = requests.get(ETHERSCAN_API_BASE, params=params)
    result = response.json()

    if result["status"] == "1" and "result" in result:
        return int(result["result"])

    return None

def get_ca_functions(abi):
    function_names = []

    # Iterate over functions in the ABI
    for function_entry in abi:
        if function_entry['type'] == 'function':
            function_name = function_entry.get('name')

            if function_name:
                function_names.append(function_name)

    return function_names

def check_eth_contract_verification(contract_address):
    url = f'https://api.etherscan.io/api'
    api_key = etherscan_api_key

    

    params_sourcecode = {
        'module': 'contract',
        'action': 'getsourcecode',
        'address': contract_address,
        'apikey': api_key,
    }

    try:
        
        response_sourcecode = requests.get(url, params=params_sourcecode)
        data_sourcecode = response_sourcecode.json()

        if data_sourcecode.get('status') == '1':
            return {
                'abi': data_sourcecode.get('result')[0].get('ABI'),
                'sourcecode': data_sourcecode.get('result')[0].get('SourceCode'),
                'proxy':data_sourcecode.get('result')[0].get('Proxy'),
                'contract_name':data_sourcecode.get('result')[0].get('ContractName'),
                'compiler':data_sourcecode.get('result')[0].get('ContractName')
            }

    except Exception as e:
        return False

    return False

def get_ai_ca_transactions(ca_address, page=1):
    params = {
        "module": "account",
        "action": "txlist",
        "address": ca_address,
        "page": page,
        "offset": 20,
        "sort": "desc",
        "apikey": etherscan_api_key,
    }

    response = requests.get(ETHERSCAN_API_BASE, params=params)
    result = response.json()
    
    if result["status"] == "1":
        return result["result"]
    else:
        return []
    
def get_internal_ai_ca_transactions(ca_address, page=1):
    params = {
        "module": "account",
        "action": "txlistinternal",
        "address": ca_address,
        "page": page,
        "offset": 20,
        "sort": "desc",
        "apikey": etherscan_api_key,
    }

    response = requests.get(ETHERSCAN_API_BASE, params=params)
    result = response.json()
    
    if result["status"] == "1":
        return result["result"]
    else:
        return []