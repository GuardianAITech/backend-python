from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv
from helpers.covalent_helpers import get_approvals, get_token_balances, get_summary_transactions, extract_token_info, extract_approvals_items,get_latest_transactions,extract_transaction_info,get_first_transaction,get_balance,calculate_total_quote
from helpers.etherscan_helpers import get_internal_transactions,get_current_block,get_block_number_3_months_ago,get_normal_transactions
import os
import asyncio

load_dotenv()
app = Flask(__name__)

covalent_api_key = os.getenv("COVALENT_API_KEY")
secret_key = os.getenv("SECRET_KEY")
chain = "eth-mainnet"

@app.route('/scan', methods=['GET'])
async def scan():
    client_key = request.headers.get('Authorization')
    if client_key != secret_key:
        abort(404)
    wallet = request.args.get('wallet')
    if not wallet:
        return jsonify({"error": "Wallet address is required"}), 400

    ### DATA for frontend previews .. quickshow  and so on ###

    approvals = get_approvals(covalent_api_key, chain, wallet)
    approvals_items = extract_approvals_items(approvals)
    token_balances = get_token_balances(covalent_api_key, chain, wallet)
    simplified_token_balances = [extract_token_info(token) for token in token_balances.get("items", [])]
    total_quote = calculate_total_quote(simplified_token_balances)
    summary_transactions = get_summary_transactions(covalent_api_key, chain, wallet)
    latest_transactions = await get_latest_transactions(covalent_api_key, chain, wallet)
    ts = await get_first_transaction(covalent_api_key, chain, wallet)
    total_balance = get_balance(covalent_api_key, chain, wallet)

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
        "last_internals":last_internals,
        "first_transaction":ts,
        "approvals": approvals_items,
        "token_balances": simplified_token_balances,
        "total_transactions": summary_transactions.get("items", [])[0].get("total_count"),
        "latest_transactions": [{"total_transaction_info": extracted_transaction_info}] + latest_transactions,
        "lastblock":current_block
    }

    return jsonify(response)



if __name__ == '__main__':
    app.run(port=5000, debug=True)
