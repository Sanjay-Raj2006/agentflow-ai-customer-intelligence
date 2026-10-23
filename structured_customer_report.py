import csv
import requests
import json
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

webhook_url = os.getenv("N8N_WEBHOOK_URL")

if not webhook_url:
    raise RuntimeError(
        "N8N_WEBHOOK_URL is missing from your .env file."
    )

# 1. Locate the existing customer dataset
csv_path = Path("d2c_customer_history_200.csv")

if not csv_path.exists():
    raise FileNotFoundError(
        f"Cannot find {csv_path}. Keep this script in your project folder."
    )

# 2. Load customer records
with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    required_columns = {
        "customer_id",
        "total_spent",
        "num_orders",
        "days_since_last_order",
    }

    if not reader.fieldnames or not required_columns.issubset(reader.fieldnames):
        raise ValueError(
            "CSV must contain: customer_id, total_spent, "
            "num_orders, days_since_last_order"
        )

    customers = list(reader)

# 3. Prepare structured customer actions
customer_actions = []
seen_ids = set()

for row in customers:
    customer_id = row["customer_id"].strip()

    if not customer_id or customer_id in seen_ids:
        continue

    seen_ids.add(customer_id)

    try:
        total_spent = float(row["total_spent"])
        num_orders = int(row["num_orders"])
        inactive_days = int(row["days_since_last_order"])
    except (ValueError, TypeError):
        print(f"Skipping {customer_id}: invalid numeric data")
        continue

    if total_spent < 0 or num_orders < 0 or inactive_days < 0:
        print(f"Skipping {customer_id}: negative customer metric")
        continue

    # 4. Assign a segment and action using explicit business rules
    if inactive_days >= 90 and total_spent >= 5000:
        segment = "Lapsed High-Value"
        priority = "High"
        action = (
            "Review for a personalized win-back campaign; "
            "check contact permissions before outreach."
        )
        reason = (
            f"Spent {total_spent:.2f} historically and has been "
            f"inactive for {inactive_days} days."
        )

    elif inactive_days >= 90:
        segment = "Lapsed Customer"
        priority = "Medium"
        action = (
            "Consider a re-engagement message with a relevant "
            "product recommendation."
        )
        reason = f"No purchase for {inactive_days} days."

    elif total_spent >= 10000 and num_orders >= 3:
        segment = "High-Value Active"
        priority = "High"
        action = (
            "Consider VIP retention, loyalty benefits, or early "
            "access to relevant products."
        )
        reason = (
            f"{num_orders} orders and {total_spent:.2f} in historical spend."
        )

    elif num_orders >= 2:
        segment = "Repeat Customer"
        priority = "Medium"
        action = (
            "Recommend relevant complementary products and measure "
            "repeat-purchase conversion."
        )
        reason = f"Has placed {num_orders} orders."

    else:
        segment = "Low-Frequency Customer"
        priority = "Medium"
        action = (
            "Test a helpful post-purchase follow-up to encourage "
            "a second order."
        )
        reason = f"Has placed {num_orders} order(s)."

    customer_actions.append({
        "customer_id": customer_id,
        "segment": segment,
        "total_spent": round(total_spent, 2),
        "num_orders": num_orders,
        "days_since_last_order": inactive_days,
        "priority": priority,
        "action_needed": action,
        "reason": reason,
        "source": "customer_history_csv",
        "status": "recommendation_only"
    })

# 5. Save the structured report
output = {
    "report_title": "Customer Growth Actions",
    "total_customers_processed": len(customer_actions),
    "note": (
        "Actions are rule-based recommendations from the supplied "
        "customer history, not guarantees of customer behavior."
    ),
    "customers": customer_actions
}

output_path = Path("structured_customer_actions.json")
output_path.write_text(
    json.dumps(output, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

# 6. Display a summary
print("===== STRUCTURED CUSTOMER REPORT =====")
print("Customers processed:", len(customer_actions))
print("Saved to:", output_path.resolve())

print("\nFirst 3 customer actions:")
for customer in customer_actions[0:20]:
    print(json.dumps(customer, indent=2, ensure_ascii=False))

 # 6. Send only 20 customer records to n8n

webhook_url = os.getenv("N8N_WEBHOOK_URL")


customers_to_send = customer_actions[:20]

payload = {"customers": customers_to_send}

try:
    response = requests.post(
        webhook_url,
        json=payload,
        timeout=30
    )
    response.raise_for_status()

    print(
        f"Request accepted: {len(customers_to_send)} customers "
        f"sent in one batch."
    )
    print("HTTP status:", response.status_code)

except requests.exceptions.Timeout:
    print("Request timed out.")
    print(
        "The batch may still have been processed by n8n. "
        "Check n8n Executions and Google Sheets before retrying."
    )

except requests.exceptions.RequestException as error:
    print("Request failed:", error)
    print(
        "Check n8n Executions and Google Sheets before retrying."
    )
