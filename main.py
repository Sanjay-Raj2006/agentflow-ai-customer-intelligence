import csv
import requests
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

def calculate_customer_metrics(customers):
    results = []

    for customer in customers:
        orders = customer["num_orders"]
        total_spent = customer["total_spent"]

        average_order_value = (
            total_spent / orders if orders > 0 else 0
        )

        results.append({
            **customer,
            "average_order_value": round(average_order_value, 2),
        })

    return results


# Load customers from the CSV
with open("d2c_customer_history_200.csv", "r", newline="", encoding="utf-8-sig") as file:
    customers = list(csv.DictReader(file))


# Convert numeric columns from text to numbers
for customer in customers:
    customer["num_orders"] = int(customer["num_orders"])
    customer["total_spent"] = float(customer["total_spent"])
    customer["days_since_last_order"] = int(
        customer["days_since_last_order"]
    )

# Calculate metrics for all CSV customers
customers = calculate_customer_metrics(customers)

print(f"Loaded and processed {len(customers)} customers")

print("\n===== CALCULATED CUSTOMER METRICS =====")
for customer in customers:
    print(customer)

# 1. Load environment variables
load_dotenv()

# 2. Get the Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Gemini API key is missing from .env")

# 3. Configure the AI model
llm = LLM(
    model="gemini/gemini-3.8-flash",
    api_key=api_key,
    temperature=1.0,
)

# 4. Create the Researcher agent
researcher = Agent(
    role="Business Prospect Researcher",
    goal=(
        "Analyze the provided business information and identify "
        "potential opportunities for AI automation services."
    ),
    backstory=(
        "You are a business research specialist helping an AI "
        "automation freelancer identify promising Indian clients. "
        "You distinguish supplied facts from assumptions and never "
        "invent missing information."
    ),
    llm=llm,
    verbose=False,
    allow_delegation=False,)

# 5. Define the customer analysis task
analysis_task = Task(
       description=(
    "Analyze the customer purchase history below.\n\n"
    f"Customer data: {customers}\n\n"
    "Identify:\n"
    "1. Frequent and high-value customers.\n"
    "2. Customers who may need re-engagement.\n"
    "3. Customers who may buy again.\n"
    "4. Practical marketing actions for each group.\n"
    "5. Any limitations in the available data.\n\n"
    "Use only the supplied data. Do not invent statistics. "
    "Explain findings in simple language that a business owner "
    "can understand. Treat recommendations as suggestions, "
    "not guaranteed outcomes."
),
expected_output=(
    "A simple customer analysis report with these sections:\n"
    "1. Business Overview: Summarize the main findings in 3 bullets.\n"
    "2. Customer Segments: Identify important customer groups.\n"
    "3. High-Value Customers: Explain which customers are valuable "
    "and why.\n"
    "4. Inactive Customers: Identify customers who may need attention.\n"
    "5. Key Findings: List the 3 most important insights.\n\n"
    "Use simple English, short sentences, clear headings, and "
    "customer IDs where available. Use actual data and numbers "
    "when supported. Avoid technical jargon, repetition, and "
    "unnecessary explanations."
),
agent=researcher,) 
    
# 6. Create the Customer Growth Strategist agent
growth_strategist = Agent(
    role="Customer Growth Strategist",
    goal=(
        "Turn customer behavior analysis into practical strategies "
        "that increase repeat purchases and customer retention."
    ),
    backstory=(
        "You are an experienced D2C growth strategist. You use "
        "customer analysis to recommend relevant, measurable actions. "
        "You never treat assumptions as proven facts."
    ),
    llm=llm,
    verbose=False,
    allow_delegation=False,
)

# 7. Define the growth strategy task
strategy_task = Task(
    description=(
    "Using the customer analysis completed by the "
    "Business Prospect Researcher, create an actionable "
    "customer growth strategy.\n\n"
    "Recommend:\n"
    "1. How to retain frequent, high-value customers.\n"
    "2. How to re-engage inactive customers.\n"
    "3. Which customers may be suitable for repeat-purchase campaigns.\n"
    "4. A practical marketing action for each group.\n\n"
    "Use only the analysis and supplied data. "
    "Do not invent customer facts or guarantee results."
),
expected_output=(
    "A practical sales and retention action plan with these sections:\n"
    "1. Top Priorities: List the 3 most important actions.\n"
    "2. Target Customers: Identify the relevant customer IDs or groups.\n"
    "3. Recommended Action: Explain what the business should do.\n"
    "4. Reason: Explain why the action may help.\n"
    "5. Success Measure: Explain how the business can measure results.\n\n"
    "Use simple English and concise bullet points. Prioritize actions "
    "by business value. Do not invent customer information, "
    "guarantee results, or repeat the entire research report."
),
agent=growth_strategist,
context=[analysis_task],)

supervisor = Agent(
    role="Senior Sales and Customer Analytics Supervisor",
    goal=(
        "Review the customer research and sales strategy, "
        "check whether the recommendations are supported by "
        "the available customer data, and produce a reliable "
        "final action plan for the business."
    ),
    backstory=(
        "You are an experienced business analyst who reviews "
        "customer insights and sales strategies. You identify "
        "unsupported assumptions, prioritize actionable "
        "recommendations, and explain the reasoning behind "
        "each important decision."
    ),
    llm=llm,
    verbose=False
)

supervisor_task = Task(
    description=(
        "Review the customer research and sales strategy "
        "provided by the previous tasks.\n\n"
        "1. Check whether the customer segments and priorities "
        "are supported by the available data.\n"
        "2. Identify any unsupported assumptions or missing information.\n"
        "3. Prioritize the recommended sales and retention actions.\n"
        "4. Explain why each priority matters to the business.\n"
        "5. Produce a clear final report with actionable next steps.\n"
        "6. Do not invent customer facts or claim that actions "
        "have been executed."
    ),
    expected_output=(
    "A concise final business report containing:\n"
    "1. Executive Summary: The 3 most important findings.\n"
    "2. Priority Actions: The 3 most useful next steps, in order.\n"
    "3. Target Customers: Relevant customer IDs or groups.\n"
    "4. Reasons: Brief explanations supported by the data.\n"
    "5. Data Limitations: Any important uncertainty or missing data.\n\n"
    "Write for a business owner with no technical background. "
    "Use simple English, clear headings, and short bullet points. "
    "Remove repetition and unsupported claims. Keep the report "
    "focused and actionable."
),
    agent=supervisor,
    context=[analysis_task, strategy_task]
)



# 8. Assemble the multi-agent crew
crew = Crew(
    agents=[researcher, growth_strategist,supervisor],
    tasks=[analysis_task, strategy_task,supervisor_task],
    process=Process.sequential,
    verbose=False,
)

# 9. Run the workflow
if __name__ == "__main__":
    result = crew.kickoff()
    print("\n===== CUSTOMER GROWTH REPORT =====\n")
    print(result.raw)

webhook_url = "N8N_WEBHOOK_URL"

report_data = {
    "message": result.raw,
    "status": "customer_growth_report"
}

response = requests.post(
    webhook_url,
    json=report_data,
    timeout=30
)

print("n8n response:", response.status_code)
print("Response body:", response.text)
