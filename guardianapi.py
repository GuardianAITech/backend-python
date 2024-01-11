from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv
from helpers.covalent_helpers import get_approvals, get_token_balances, get_summary_transactions, extract_token_info, extract_approvals_items,get_latest_transactions,extract_transaction_info
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

    approvals = get_approvals(covalent_api_key, chain, wallet)
    approvals_items = extract_approvals_items(approvals)
    token_balances = get_token_balances(covalent_api_key, chain, wallet)
    simplified_token_balances = [extract_token_info(token) for token in token_balances.get("items", [])]
    summary_transactions = get_summary_transactions(covalent_api_key, chain, wallet)
    latest_transactions = await get_latest_transactions(covalent_api_key, chain, wallet)

    extracted_transaction_info = extract_transaction_info(latest_transactions)

    total_balance = sum(
        float(token.get("pretty_quote", "0").replace('$', '').replace(',', '')) 
        if token and token.get("pretty_quote") is not None 
        else 0 
        for token in token_balances.get("items", [])
    )

    total_balance_dict = {"total_balance": total_balance}
    
    simplified_token_balances.append(total_balance_dict)

    response = {
        "approvals": approvals_items,
        "token_balances": simplified_token_balances,
        "total_transactions": summary_transactions.get("items", [])[0].get("total_count"),
        "latest_transactions": [{"total_transaction_info": extracted_transaction_info}] + latest_transactions
    }

    return jsonify(response)



if __name__ == '__main__':
    app.run(port=5000, debug=True)
