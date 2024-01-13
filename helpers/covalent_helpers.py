from covalent import CovalentClient
from dotenv import load_dotenv
from helpers.data_converter import convert_to_dict
import asyncio
import os
import requests
from requests.auth import HTTPBasicAuth

load_dotenv()
covalent_api_key = os.getenv("COVALENT_API_KEY")
chain = os.getenv("CHAIN")

def get_balance(wallet):
    c = CovalentClient(covalent_api_key)
    response = c.balance_service.get_native_token_balance(chain, wallet)
    
    if response and not response.error:
        data = convert_to_dict(response.data)
        if "items" in data and data["items"]:
            balance_info = data["items"][0]
            balance_wei = balance_info.get("balance", "0")
            quote = balance_info.get("quote", 0)
            
            balance_ether = float(balance_wei) / 10**18
            
            return {
                "balance_ether": balance_ether,
                "quote": quote,
            }

    return {"error": "Unable to process the request"}

def get_approvals(wallet):
    c = CovalentClient(covalent_api_key)
    response = c.security_service.get_approvals(chain, wallet)
    return convert_to_dict(response.data) if response and not response.error else {"error": "Unable to process the request"}

def get_token_balances(wallet):
    c = CovalentClient(covalent_api_key)
    response = c.balance_service.get_token_balances_for_wallet_address(chain, wallet, no_spam=True)
    return convert_to_dict(response.data) if response and not response.error else {"error": "Unable to process the request"}

def get_summary_transactions(wallet):
    c = CovalentClient(covalent_api_key)
    response = c.transaction_service.get_transaction_summary(chain, wallet)
    return convert_to_dict(response.data) if response and not response.error else {"error": "Unable to process the request"}

def get_transactions_paginated(wallet, page):
    url = f"https://api.covalenthq.com/v1/eth-mainnet/address/{wallet}/transactions_v3/page/{page}/?with-safe=true"
    headers = {
        "accept": "application/json",
    }
    basic = HTTPBasicAuth(covalent_api_key, '')
    response = requests.get(url, headers=headers, auth=basic)

    return response.json() if response else {"data": {"items": []}}

async def get_first_transaction(wallet):
    c = CovalentClient(covalent_api_key)
    try:
        transactions = []
        i = 0
        async for res in c.transaction_service.get_all_transactions_for_address(chain, wallet, quote_currency="USD", block_signed_at_asc=True, with_safe=True, no_logs=True):
            response_data = convert_to_dict(res)
            transactions.append(response_data)
            i = i + 1
            if i == 1:
                break

        return transactions
           
    except Exception as e:
        print(e)


async def get_latest_transactions(wallet, limit=20):
    c = CovalentClient(covalent_api_key)
    try:
            transactions = []
            i = 0
            async for res in c.transaction_service.get_all_transactions_for_address(chain, wallet, quote_currency="USD",no_logs=True,with_safe=True):
                response_data = convert_to_dict(res)
                transactions.append(response_data)
                i = i+1
                if i == 30:
                    break
            return transactions
    except Exception as e:
            print(e)


def get_spam(wallet):
    c = CovalentClient(covalent_api_key)
    response = c.balance_service.get_token_balances_for_wallet_address(chain, wallet, no_spam=False)
    return convert_to_dict(response.data) if response and not response.error else {"error": "Unable to process the request"}




