from flask import Flask, request, jsonify, abort
import json
from dotenv import load_dotenv
from helpers.covalent_helpers import get_approvals, get_token_balances, get_summary_transactions,get_transactions_paginated,get_latest_transactions,get_first_transaction,get_balance,get_spam
from helpers.etherscan_helpers import get_internal_transactions,get_current_block,get_block_number_3_months_ago,get_normal_transactions
from helpers.filters import extract_token_info, extract_approvals_items,extract_transaction_info,calculate_total_quote,filter_spam_and_dust_items,compare_transaction_times,filter_token_balances,filter_spam_and_dust_items_ai,filter_latest_transactions_for_ai,filter_approvals_ai
from helpers.data_converter import compare_last_scan
from helpers.database import get_latest_last_scan,save_response_to_database
from helpers.mongodb_installer import prepare_mongodb
from ai.ai_transaction_analyzer import get_transaction_details
from ai.ai_wallet_analyzer import check_wallet_with_ai
from ai.ai_contract_analyzer import ai_analyze_contract

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
    ai_approvals = filter_approvals_ai(approvals)
    approvals_items = extract_approvals_items(approvals)
    token_balances = get_token_balances(wallet)
    ai_bal = filter_token_balances(token_balances)
    simplified_token_balances = [
        extract_token_info(token)
        for token in token_balances.get("items", [])
        if token.get("balance", 0) != 0
    ]
    total_quote = calculate_total_quote(simplified_token_balances)
    summary_transactions = get_summary_transactions(wallet)
    summary_items = summary_transactions.get("items", [])
    latest_transactions = await get_latest_transactions(wallet)
    ts = await get_first_transaction(wallet)
    total_balance = get_balance(wallet)

    spam = get_spam(wallet)
    spam_filtered = filter_spam_and_dust_items(spam)
    ai_spam = filter_spam_and_dust_items_ai(spam)

    extracted_transaction_info = extract_transaction_info(latest_transactions)
    ai_trans = filter_latest_transactions_for_ai(latest_transactions)

    current_block = get_current_block()
    ago_block = get_block_number_3_months_ago()
    last_internals = get_internal_transactions(wallet, ago_block, current_block, page=1)
    entries = len(last_internals)
    last_internals.append({"total": entries})


    total_balance_dict = {"total_balance": total_balance, "total_asset_quote":total_quote}
    
    simplified_token_balances.append(total_balance_dict)
    last_activity_info = compare_transaction_times(latest_transactions, last_internals)

    
    ##### Data for security checks ####
    normal_transactions = get_normal_transactions(wallet, ago_block, current_block, page=1)

    aidatas = {
        "spam": ai_spam,
        "last_internals":last_internals,
        "approvals": ai_approvals,
        "token_balances": ai_bal,
        "total_transactions": summary_items[0].get("total_count") if summary_items else 0,
        "latest_transactions": [{"gas_info_and_total_info": extracted_transaction_info}] + ai_trans,
    }

    response = {
        "spam": spam_filtered,
        "last_internals":last_internals,
        "first_transaction":ts,
        "approvals": approvals_items,
        "token_balances": simplified_token_balances,
        "total_transactions": summary_items[0].get("total_count") if summary_items else 0,
        "latest_transactions": [{"total_transaction_info": extracted_transaction_info}] + latest_transactions,
        "lastblock":current_block,
        "last_activity":last_activity_info
    }
    response["last_scan"] = {
            "last_total_native_balance": total_balance.get("balance_ether"),
            "last_total_native_value": total_balance.get("quote"),
            "last_total_assets_value": total_quote,
            "last_approval_count": len(approvals_items["items"]),
            "last_dust_count": spam_filtered.get("dust_count"),
            "last_spam_count": spam_filtered.get("spam_count"),
            "last_total_at_risk": approvals_items.get("total_at_risk"),
            "last_total_transactions": summary_items[0].get("total_count") if summary_items else 0,
            "last_block": current_block
        }
    
    
    lastscan = get_latest_last_scan(wallet)

    if lastscan:
        updated_response = compare_last_scan(lastscan,response["last_scan"])
        response["calculations"] = updated_response 

    ainalyze = check_wallet_with_ai(aidatas)
    response["ai"] = ainalyze
    
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

@app.route('/get_approvals', methods=['GET'])
async def get_approvalx():
    client_key = request.headers.get('Authorization')
    if client_key != secret_key:
        abort(404)
    wallet = request.args.get('wallet')
    
    if not wallet:
        return jsonify({"error": "Wallet address is required"}), 400
    approvals = get_approvals(wallet)
    approvals_items = extract_approvals_items(approvals)
    response = {
       
        "approvals": approvals_items,
        
    }
    return jsonify(response)


@app.route('/analyze_transaction/<transaction_hash>', methods=['GET'])
def analyze_transaction(transaction_hash):
    client_key = request.headers.get('Authorization')
    if client_key != secret_key:
        abort(404)
    transaction_details = get_transaction_details(transaction_hash)
    return jsonify(transaction_details)

@app.route('/analyze_contract/<contract>', methods=['GET'])
def analyze_contract(contract):
    client_key = request.headers.get('Authorization')
    if client_key != secret_key:
        abort(404)
    canalyze = ai_analyze_contract(contract)
    return jsonify(canalyze)

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(port=port, debug=True)
