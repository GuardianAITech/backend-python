from covalent import CovalentClient
from helpers.data_converter import convert_to_dict

def get_approvals(covalent_api_key, chain, wallet):
    c = CovalentClient(covalent_api_key)
    response = c.security_service.get_approvals(chain, wallet)
    return convert_to_dict(response.data) if response and not response.error else {"error": "Unable to process the request"}

def get_token_balances(covalent_api_key, chain, wallet):
    c = CovalentClient(covalent_api_key)
    response = c.balance_service.get_token_balances_for_wallet_address(chain, wallet, no_spam=True)
    return convert_to_dict(response.data) if response and not response.error else {"error": "Unable to process the request"}

def get_summary_transactions(covalent_api_key, chain, wallet):
    c = CovalentClient(covalent_api_key)
    response = c.transaction_service.get_transaction_summary(chain, wallet)
    return convert_to_dict(response.data) if response and not response.error else {"error": "Unable to process the request"}

def extract_token_info(token):
    return {
        "balance": token.get("balance", 0),
        "contract_address": token.get("contract_address", ""),
        "decimals": token.get("contract_decimals", 0),
        "contract_name": token.get("contract_name", ""),
        "contract_ticker_symbol": token.get("contract_ticker_symbol", ""),
        "logo_url": token.get("logo_url", ""),
        "native_token": token.get("native_token", False),
        "pretty_quote": token.get("pretty_quote", ""),
        "quote_rate": token.get("quote_rate", 0.0),
    }

def extract_approvals_items(approvals):
    return approvals.get("items", [])