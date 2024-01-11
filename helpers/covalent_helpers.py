from covalent import CovalentClient
from helpers.data_converter import convert_to_dict
import asyncio

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

async def get_latest_transactions(covalent_api_key, chain, wallet, limit=20):
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


def extract_token_info(token):
    return {
        "balance": token.get("balance", 0),
        "contract_address": token.get("contract_address", ""),
        "decimals": token.get("contract_decimals", 0),
        "contract_name": token.get("contract_name", ""),
        "contract_ticker_symbol": token.get("contract_ticker_symbol", ""),
        "logo_url": token.get("logo_url", ""),
        "native_token": token.get("native_token", False),
        "pretty_quote": float(token.get("pretty_quote", "0").replace('$', '').replace(',', '')) if token.get("pretty_quote") is not None else 0,
        "quote_rate": token.get("quote_rate", 0.0),
    }

def extract_transaction_info(transactions):
    total_gas_spent = sum(t.get("gas_spent", 0) for t in transactions)
    total_gas_quote = sum(float(t.get("gas_quote", 0)) for t in transactions)
    total_successful = sum(1 for t in transactions if t.get("successful", False))
    total_failed = sum(1 for t in transactions if not t.get("successful", False))
    total_value = sum(float(t.get("value_quote", 0)) for t in transactions)

    totals_dict = {
        "total_gas_spent": total_gas_spent,
        "total_gas_quote": total_gas_quote,
        "total_successful": total_successful,
        "total_failed": total_failed,
        "total_value": total_value,
    }

    return totals_dict




def extract_approvals_items(approvals):
    items = approvals.get("items", [])
    total_at_risk = sum(float(approval.get("pretty_value_at_risk_quote", "0").replace('$', '').replace(',', '')) if approval.get("pretty_value_at_risk_quote") is not None else 0 for approval in items)
    return {
        "items": items,
        "total_at_risk": total_at_risk
    }

