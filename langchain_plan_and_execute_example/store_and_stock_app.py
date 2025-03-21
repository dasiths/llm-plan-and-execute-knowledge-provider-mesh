from flask import Flask, request, jsonify
import json
import copy

app = Flask(__name__)

all_stores = [
    { "store_id": "101", "store_name": "Hardy Bayswater", "address": "200 Canterbury Rd, Bayswater VIC 3153"},
    { "store_id": "102", "store_name": "Hardy Ringwood", "address": "123 Charter St, Ringwood VIC 3134"},
    { "store_id": "103", "store_name": "Hardy Glen Waverley", "address": "1 Railway Pde, Glen Waverley VIC 3150"},
    { "store_id": "104", "store_name": "Hardy Chadstone", "address": "345 Bay Rd, Chadstone VIC 3148"},
    { "store_id": "105", "store_name": "Hardy Berwick", "address": "12 Bulla Rd, Berwick VIC 3806"},
]

all_stock_items = [
    {"item_description": "Ryobi One Plus 18V Drill", "item_code": "RYB-DRILL"},
    {"item_description": "Osmocote Organic Fertilizer 1kg", "item_code": "ORG-FERT"},
]

stock_qty = [
    {"store_id": "101", "item_code": "RYB-DRILL", "qty": 10},
    {"store_id": "101", "item_code": "ORG-FERT", "qty": 0},
    {"store_id": "102", "item_code": "RYB-DRILL", "qty": 0},
    {"store_id": "102", "item_code": "ORG-FERT", "qty": 5},
    {"store_id": "103", "item_code": "RYB-DRILL", "qty": 0},
    {"store_id": "103", "item_code": "ORG-FERT", "qty": 1},
    {"store_id": "104", "item_code": "RYB-DRILL", "qty": 10},
    {"store_id": "104", "item_code": "ORG-FERT", "qty": 2},
    {"store_id": "105", "item_code": "RYB-DRILL", "qty": 2},
    {"store_id": "105", "item_code": "ORG-FERT", "qty": 0}
]

def get_all_stores(action_input: dict) -> str:
    result = json.dumps(all_stores)
    return f"""
Here are the store_id and other information.
'store_id' is required for subsequent API calls.
Please remember it and display with the store name when providing information to the user.

i.e. Hardy Bayswater (ID:101), Hardy Ringwood (ID:102), etc.

{result}
"""

def find_closest_store(action_input: dict) -> str:
    # mock distances
    stores = copy.deepcopy(all_stores)
    for index, store in enumerate(stores):
        store["distance_km"] = index + 5

    result = json.dumps(stores)
    return f"""
Here are the store_id and other information.
'store_id' is required for subsequent API calls.
Please remember it and display with the store name when providing information to the user.

i.e. Hardy Bayswater (ID:101), Hardy Ringwood (ID:102), etc.

{result}
"""

def find_available_stock(action_input: dict) -> str:
    store = action_input["store_id"] if "store_id" in action_input else None
    item_code = action_input["item_code"]

    if not " " in item_code and len(item_code) > 12:
        return "Sorry, item_code must be a maximum of 12 characters and looks to be incorrect. Please use the find item API to retrieve the correct item_code."

    if store:
        if not store.isnumeric() and not len(store) == 3:
            return "Sorry, store_id must be a number. Use the get all stored API to retrieve the store ids."

        items_in_store = [item for item in stock_qty if item["store_id"] == store and item["item_code"] == item_code]
    else:
        items_in_store = [item for item in stock_qty if item["item_code"] == item_code]

    if len(items_in_store) > 0:
        return json.dumps(items_in_store)

    return f"Sorry, {item_code} is not available in any store."

def find_item(action_input: dict) -> str:
    query: str = action_input["query"].lower()
    results = [item for item in all_stock_items if item["item_code"].lower() == query or
               any(word in item["item_description"].lower() for word in query.split(" "))]

    if len(results) > 0:
        return json.dumps(results)

    return f"Sorry, there is no matching item with '{query}' in any store."

### API Endpoints ###

@app.route('/get_all_stores', methods=['POST'])
def process_list_stores():
    try:
        data = request.get_json()  # Get JSON payload from the request
        print(data)

        if data is None:
            return jsonify({'error': 'No JSON data provided'}), 400

        result = {}
        result["output"] = get_all_stores(data["payload"])

        return jsonify(result)  # Sending back the JSON payload as response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/find_closest_store', methods=['POST'])
def process_closest_store():
    try:
        data = request.get_json()  # Get JSON payload from the request
        print(data)

        if data is None:
            return jsonify({'error': 'No JSON data provided'}), 400

        result = {}
        result["output"] = find_closest_store(data["payload"])

        return jsonify(result)  # Sending back the JSON payload as response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/find_available_stock', methods=['POST'])
def process_find_available_stock():
    try:
        data = request.get_json()  # Get JSON payload from the request
        print(data)

        if data is None:
            return jsonify({'error': 'No JSON data provided'}), 400

        result = {}
        result["output"] = find_available_stock(data["payload"])

        return jsonify(result)  # Sending back the JSON payload as response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/find_item', methods=['POST'])
def process_find_item():
    try:
        data = request.get_json()  # Get JSON payload from the request
        print(data)

        if data is None:
            return jsonify({'error': 'No JSON data provided'}), 400

        result = {}
        result["output"] = find_item(data["payload"])

        return jsonify(result)  # Sending back the JSON payload as response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50002, debug=True)
