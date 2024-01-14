from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv
from helpers.covalent_helpers import get_approvals, get_token_balances, get_summary_transactions,get_transactions_paginated,get_latest_transactions,get_first_transaction,get_balance,get_spam
from helpers.etherscan_helpers import get_internal_transactions,get_current_block,get_block_number_3_months_ago,get_normal_transactions
from helpers.filters import extract_token_info, extract_approvals_items,extract_transaction_info,calculate_total_quote,filter_spam_and_dust_items
from helpers.data_converter import compare_last_scan
from helpers.database import get_latest_last_scan,save_response_to_database
from helpers.mongodb_installer import prepare_mongodb
import os
import asyncio


load_dotenv()
app = Flask(__name__)


secret_key = os.getenv("SECRET_KEY")
prepare_mongodb()

@app.route('/scan', methods=['GET'])
async def scan():
    client_key = request.headers.get('Authorization')
    if client_key != secret_key:
        abort(404)
    wallet = request.args.get('wallet')
    if not wallet:
        return jsonify({"error": "Wallet address is required"}), 400

    ### DATA for frontend previews .. quickshow  and so on ###

    approvals = get_approvals(wallet)
    approvals_items = extract_approvals_items(approvals)
    token_balances = get_token_balances(wallet)
    simplified_token_balances = [
        extract_token_info(token)
        for token in token_balances.get("items", [])
        if token.get("balance", 0) != 0
    ]
    total_quote = calculate_total_quote(simplified_token_balances)
    summary_transactions = get_summary_transactions(wallet)
    latest_transactions = await get_latest_transactions(wallet)
    ts = await get_first_transaction(wallet)
    total_balance = get_balance(wallet)

    spam = get_spam(wallet)
    spam_filtered = filter_spam_and_dust_items(spam)
   

    extracted_transaction_info = extract_transaction_info(latest_transactions)

    current_block = get_current_block()
    ago_block = get_block_number_3_months_ago()
    last_internals = get_internal_transactions(wallet, ago_block, current_block, page=1)
    entries = len(last_internals)
    last_internals.append({"total": entries})


    total_balance_dict = {"total_balance": total_balance, "total_asset_quote":total_quote}
    
    simplified_token_balances.append(total_balance_dict)



    ##### Data for security checks ####
    normal_transactions = get_normal_transactions(wallet, ago_block, current_block, page=1)

    response = {
        "spam": spam_filtered,
        "last_internals":last_internals,
        "first_transaction":ts,
        "approvals": approvals_items,
        "token_balances": simplified_token_balances,
        "total_transactions": summary_transactions.get("items", [])[0].get("total_count"),
        "latest_transactions": [{"total_transaction_info": extracted_transaction_info}] + latest_transactions,
        "lastblock":current_block
    }
    response["last_scan"] = {
            "last_total_native_balance": total_balance.get("balance_ether"),
            "last_total_native_value": total_balance.get("quote"),
            "last_total_assets_value": total_quote,
            "last_approval_count": len(approvals_items["items"]),
            "last_dust_count": spam_filtered.get("dust_count"),
            "last_spam_count": spam_filtered.get("spam_count"),
            "last_total_at_risk": approvals_items.get("total_at_risk"),
            "last_total_transactions": summary_transactions.get("items", [])[0].get("total_count"),
            "last_block": current_block
        }
    
    
    lastscan = get_latest_last_scan(wallet)

    if lastscan:
        updated_response = compare_last_scan(lastscan,response["last_scan"])
        response["calculations"] = updated_response 
    
    save_response_to_database(wallet, response)

    return jsonify(response)


@app.route('/get_transactions', methods=['GET'])
async def get_transactions():
    client_key = request.headers.get('Authorization')
    if client_key != secret_key:
        abort(404)
    wallet = request.args.get('wallet')
    page = request.args.get('page')
    if not wallet:
        return jsonify({"error": "Wallet address is required"}), 400
    if not page:
        page = 0
    transactions = get_transactions_paginated(wallet, page)
    
    items = transactions.get("data", {}).get("items")
    
    items = items if isinstance(items, list) else []
    
    response = {"items": items}
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(port=port, debug=True)
