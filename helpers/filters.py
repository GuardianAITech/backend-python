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
