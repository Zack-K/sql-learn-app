import json
import os

drills_path = 'data/drills.json'

with open(drills_path, 'r', encoding='utf-8') as f:
    drills = json.load(f)

# Define mock_data for each schema
mock_data_map = {
    "users.csv": [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"}
    ],
    "transactions": [
        {"transaction_id": 101, "user_id": 1, "amount": 1500, "transaction_date": "2023-10-01"},
        {"transaction_id": 102, "user_id": 2, "amount": -500, "transaction_date": "2023-10-02"},
        {"transaction_id": 103, "user_id": 1, "amount": 2000, "transaction_date": "2099-12-31"}
    ],
    "sales": [
        {"sale_id": 1, "store_id": 10, "amount": 5000, "currency": "JPY", "created_at": "2023-10-01"},
        {"sale_id": 2, "store_id": 10, "amount": 100, "currency": "USD", "created_at": "2023-10-01"},
        {"sale_id": 3, "store_id": 11, "amount": 3000, "currency": "JPY", "created_at": "2023-10-02"}
    ],
    "orders": [
        {"order_id": 1, "customer_id": 1, "status": "completed", "amount": 1000, "ordered_at": "2023-10-01"},
        {"order_id": 2, "customer_id": 2, "status": "pending", "amount": 500, "ordered_at": "2023-10-02"},
        {"order_id": 3, "customer_id": 1, "status": "completed", "amount": 2000, "ordered_at": "2023-10-03"}
    ],
    "purchases": [
        {"purchase_id": 1, "customer_id": 1, "amount": 1200, "item_name": "Book"},
        {"purchase_id": 2, "customer_id": 2, "amount": 800, "item_name": "Pen"},
        {"purchase_id": 3, "customer_id": 1, "amount": 300, "item_name": "Notebook"}
    ],
    "customers": [
        {"customer_id": 1, "name": "Alice", "email": "alice@example.com"},
        {"customer_id": 2, "name": "Bob", "email": "bob@example.com"}
    ],
    "orders.csv": [
        {"order_id": 1, "customer_id": 1, "status": "completed", "amount": 1000},
        {"order_id": 2, "customer_id": 2, "status": "pending", "amount": 500},
        {"order_id": 3, "customer_id": 99, "status": "completed", "amount": 2000}
    ],
    "customers.csv": [
        {"customer_id": 1, "name": "Alice"},
        {"customer_id": 2, "name": "Bob"}
    ],
    "API Endpoint": [
        {"GET /api/v1/sales_data": "Returns daily sales JSON array"}
    ],
    "sales (Partitioned by Date)": [
        {"sale_id": 1, "amount": 1500, "sale_date (YYYY-MM-DD)": "2023-10-01"},
        {"sale_id": 2, "amount": 2000, "sale_date (YYYY-MM-DD)": "2023-10-02"}
    ],
    "holidays_master": [
        {"holiday_date": "2023-10-09", "description": "Sports Day"}
    ],
    "dest_table (既存データ)": [
        {"id": 1, "val": "A", "updated_at": "2023-10-01 10:00:00"},
        {"id": 2, "val": "B", "updated_at": "2023-10-01 11:00:00"}
    ],
    "new_data (今日の抽出データ)": [
        {"id": 2, "val": "B_updated", "updated_at": "2023-10-02 10:00:00"},
        {"id": 3, "val": "C", "updated_at": "2023-10-02 10:05:00"}
    ],
    "raw_json_events (入力)": [
        {"user": "A", "items (Array)": "['apple', 'banana']"},
        {"user": "B", "items (Array)": "['orange']"}
    ],
    "fct_orders (検証対象)": [
        {"order_id": "O1", "customer_id": 1, "amount": 1000, "status": "completed"},
        {"order_id": "O1", "customer_id": 1, "amount": 500, "status": "pending"},
        {"order_id": "O2", "customer_id": 2, "amount": None, "status": "completed"}
    ]
}

for drill in drills:
    schemas = drill.get('schema', [])
    for s in schemas:
        tname = s.get('table_name')
        if tname in mock_data_map:
            s['mock_data'] = mock_data_map[tname]
        elif tname == "[出力] customer_sales.csv":
            pass # No mock data for output
        elif "Task:" in tname or "Source" in tname or "DAG" in tname or "ソース (Raw)" in tname or "変換層 (Models)" in tname or "Data Warehouse Tables" in tname:
            pass # Conceptual mock data not needed for raw sql execution in these conceptual days (DAG, DWH)
        
with open(drills_path, 'w', encoding='utf-8') as f:
    json.dump(drills, f, ensure_ascii=False, indent=2)

print("Drill data updated with mock data.")
