
weights = {
    "approvals": 8,
    "balance_changes": 9,
    "token_transfers": 7,
    "contract_events": 6,
    "internal_transactions": 8,
    "nonce": 9,
    "code_metadata": 7,
    "internal_contracts": 8,
    "account_transactions": 8,
    "contract_source_code": 9,
    "token_approvals": 8,
    "code_size": 7,
    "gas_usage": 8,
    "event_logs": 7,
    "smart_contract_calls": 8,
}

def calculate_safety_score(transaction_details):
    total_weight = sum(weights.values())
    safety_score = sum(weights[param] * int(transaction_details.get(param, 0) != "") for param in weights) / total_weight

    return safety_score