from datetime import datetime, timedelta, timezone

def extract_token_info(token):
    balance = token.get("balance", 0)
    
    return {
        "balance": balance,
        "contract_address": token.get("contract_address", ""),
        "decimals": token.get("contract_decimals", 0),
        "contract_name": token.get("contract_name", ""),
        "contract_ticker_symbol": token.get("contract_ticker_symbol", ""),
        "logo_url": token.get("logo_url", ""),
        "native_token": token.get("native_token", False),
        "pretty_quote": float(token.get("pretty_quote", "0").replace('$', '').replace(',', '')) if token.get("pretty_quote") is not None else 0,
        "quote_rate": token.get("quote_rate", 0.0),
    }

def calculate_total_quote(simplified_token_balances):
    total_quote = 0.0

    for token in simplified_token_balances:
        if token is not None:
            if not token["native_token"] and token["pretty_quote"] is not None:
                total_quote += token["pretty_quote"]

    return total_quote

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

def convert_booleans(entry):
    if isinstance(entry, list):
        return [convert_booleans(item) for item in entry]
    elif isinstance(entry, dict):
        return {key: convert_booleans(value) for key, value in entry.items()}
    elif isinstance(entry, str) and entry.lower() in ('true', 'false'):
        return entry.lower() == 'true'
    return entry

def filter_approvals_ai(approvals):
    filtered_approvals = [
        {
            'balance_quote': item.get('balance_quote'),
            'spenders': [
                {
                    'allowance': spender.get('allowance'),
                    'block_signed_at': spender.get('block_signed_at'),
                    'risk_factor': spender.get('risk_factor'),
                    
                }
                for spender in item.get('spenders', [])
            ],
            'ticker_symbol': item.get('ticker_symbol')
        }
        for item in approvals.get('items', [])
    ]
    return filtered_approvals


def extract_approvals_items(approvals):
    items = approvals.get("items", [])
    total_at_risk = sum(float(approval.get("pretty_value_at_risk_quote", "0").replace('$', '').replace(',', '')) if approval.get("pretty_value_at_risk_quote") is not None else 0 for approval in items)
    return {
        "items": items,
        "total_at_risk": total_at_risk
    }

def filter_spam_and_dust_items(data):
    if "items" in data:
        spam_items = [item for item in data["items"] if item.get("is_spam")]
        dust_items = [item for item in data["items"] if item.get("type") == "dust"]

        return {
            "spam_count": len(spam_items),
            "spam_items": spam_items,
            "dust_count": len(dust_items),
            "dust_items": dust_items
        }
    else:
        return {"spam_count": 0, "spam_items": [], "dust_count": 0, "dust_items": []}

def filter_spam_and_dust_items_ai(data):
    if "items" in data:
        spam_items = [item for item in data["items"] if item.get("is_spam")]

        # Adjusted filtering for dust items
        dust_items = [
            {
                'balance': item['balance'],
                'contract_name': item['contract_name'],
                'last_transferred_at': item['last_transferred_at']
            }
            for item in data["items"] if item.get("type") == "dust"
        ]

        return {
            "spam_count": len(spam_items),
            "spam_items": spam_items,
            "dust_count": len(dust_items),
            "dust_items": dust_items
        }
    else:
        return {"spam_count": 0, "spam_items": [], "dust_count": 0, "dust_items": []}  

def compare_transaction_times(transactions, internal_transactions):
    if not transactions or not internal_transactions:
        return {"error": "No transactions or internal transactions provided"}

    latest_transaction_time = get_latest_timestamp(transactions)
    latest_internal_time = get_latest_timestamp(internal_transactions)

    if latest_transaction_time is None and latest_internal_time is None:
        return {"error": "No valid timestamps found"}

    if latest_transaction_time is None:
        latest_time = latest_internal_time
    elif latest_internal_time is None:
        latest_time = latest_transaction_time
    else:
        latest_time = max(latest_transaction_time, latest_internal_time)

    if latest_time is None:
        return {"error": "No valid timestamps found"}

    time_difference = datetime.now(timezone.utc) - latest_time
    days_ago = time_difference.days
    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    response = {
        "days_ago": days_ago,
        "hours_ago": hours,
        "minutes_ago": minutes,
        "seconds_ago": seconds,
        "sentence": f"The wallet was used {days_ago} days, {hours} hours, {minutes} minutes, and {seconds} seconds ago."
    }

    if days_ago >= 90:
        response["warning"] = "This wallet could be inactive."

    return response

def get_latest_timestamp(transactions):
    timestamps = [transaction.get("block_signed_at") for transaction in transactions if transaction.get("block_signed_at")]
    timestamps = [timestamp for timestamp in timestamps if timestamp]

    if timestamps:
        return max(timestamps)

    return None

def filter_token_balances(token_balances):
    filtered_balances = [
        {
            'balance': token.get('balance'),
            'contract_ticker_symbol': token.get('contract_ticker_symbol')
        }
        for token in token_balances.get("items", [])
    ]
    return filtered_balances

def filter_latest_transactions_for_ai(latest_transactions):
    filtered_transactions = [
        {
            'block_height': transaction.get('block_height'),
            'block_signed_at': transaction.get('block_signed_at'),
            'fees_paid': transaction.get('fees_paid'),
            'from_address': transaction.get('from_address'),
            'gas_spent': transaction.get('gas_spent'),
            'successful': transaction.get('successful'),
            'to_address': transaction.get('to_address'),
            'value': transaction.get('value'),
            'value_quote': transaction.get('value_quote'),
            'dex_details': transaction.get('dex_details'),
            'lending_details': transaction.get('lending_details'),
            'log_events': transaction.get('log_events')
        }
        for transaction in latest_transactions
    ]
    return filtered_transactions



