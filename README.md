# AI-Powered Customer Growth Automation

An end-to-end customer-growth automation project combining CrewAI multi-agent orchestration, Python data processing, n8n workflow automation, and Google Sheets.

## Project Overview

This project demonstrates how customer purchase history can be analyzed to identify customer segments, prioritize follow-up opportunities, and generate actionable customer-growth recommendations.

The system processes customer data, produces structured customer actions, and sends a batch of selected records to an n8n webhook. n8n then processes the records and updates Google Sheets without creating duplicate rows for existing customers.

**Project status:** Core workflow implemented and end-to-end batch processing tested.

## Business Problem

Businesses often have customer data but lack an efficient process for turning that data into actionable follow-up recommendations.

This project demonstrates an automated workflow that helps organize customer-growth opportunities and synchronize recommended actions with a spreadsheet-based CRM.

## Architecture

```text
Customer History CSV
        |
        v
CrewAI Multi-Agent Analysis
        |
        v
Customer-Growth Recommendations
        |
        v
Python Structured Processing
        |
        v
structured_customer_actions.json
        |
        v
Select Up to 20 Customer Records
        |
        v
n8n Production Webhook
        |
        v
Split Out Customer Records
        |
        v
Google Sheets: Append or Update Row
        |
        v
Updated Customer CRM
```

## Technology Stack

- **Python** — Data processing and integration logic.
- **CrewAI** — Multi-agent orchestration for customer analysis and strategy.
- **Google Gemini** — Language model provider used for agent tasks.
- **n8n** — Workflow automation and webhook-based integration.
- **Google Sheets** — Customer action tracking and CRM-style record management.
- **Pandas / CSV and JSON** — Customer data handling, where used in the implementation.
- **Python Requests** — HTTP requests to the n8n webhook.

## Multi-Agent Design

The CrewAI project includes three agent roles:

- **Researcher:** Analyzes the customer information and relevant patterns.
- **Growth Strategist:** Develops customer-growth recommendations.
- **Supervisor:** Reviews the preceding task outputs through the configured workflow.

The agents and their tasks are orchestrated using CrewAI. The downstream Python processing and n8n integration handle the structured data delivery.

## Data Processing

The project uses a sample customer-history dataset containing 200 fictional customers.

The dataset includes customer information such as purchase history and customer activity. Python processing prepares structured customer actions for downstream automation.

The structured output is stored in:

`structured_customer_actions.json`

The Python integration script is:

`structured_customer_report.py`

The integration selects up to 20 customer records for each submitted batch.

**Data note:** The dataset contains fictional sample customers and is intended for demonstration and testing, not real customer decision-making.

## n8n Workflow

The production workflow uses the following nodes:

1. **Webhook** — Receives the customer batch from Python.
2. **Split Out** — Separates the `customers` array into individual customer records.
3. **Google Sheets** — Appends new records or updates existing records using `Customer ID` as the matching field.

The workflow has been tested with a batch of 20 customer records. The request returned HTTP 200, and existing records were updated without creating duplicates.

### Reliability Configuration

The Google Sheets node is configured with retry-on-failure enabled, a maximum-tries setting of 3, and a 1,000 ms wait between tries.

A permission-related failure was reproduced during testing, and access was restored successfully. The workflow subsequently executed successfully. The individual retry attempts were not independently verified.

## Setup

### 1. Clone or copy the project

Open the project folder in VS Code.

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

If the project contains a `requirements.txt` file:

```powershell
pip install -r requirements.txt
```

Otherwise, use the dependency versions already installed and tested in the project. Create a dependency file before setting up the project on another machine.

### 4. Configure environment variables

Create or update the local `.env` file with the required credentials and configuration, including:

```text
GEMINI_API_KEY=your_gemini_api_key
N8N_WEBHOOK_URL=your_n8n_production_webhook_url
```

Use the exact environment-variable names expected by the existing code. Other required settings may depend on the CrewAI entry point.

Never commit real API keys, webhook URLs containing secrets, or other credentials to a public repository.

### 5. Verify the Python integration script

Run the syntax check:

```powershell
python -m py_compile structured_customer_report.py
```

Then, after confirming the required environment variables and n8n workflow are configured, run the integration script:

```powershell
python structured_customer_report.py
```

Run the CrewAI analysis using the project's existing CrewAI entry point before the integration step if the analysis has not already been executed. The entry-point filename should match the actual file in the project.

## Testing Results

| Test | Result |
|---|---|
| Python syntax check | Passed |
| Production webhook request | HTTP 200 |
| Batch of 20 customer records | Passed |
| Existing customer updates | Passed |
| Duplicate prevention using Customer ID | Passed |
| Test workflow after permission restoration | Passed |
| All three retry attempts independently verified | Not verified |

## Project Structure

Key files include:

```text
multi_agent_orchestration_crewai/
├── .env
├── .gitignore
├── .venv/
├── d2c_customer_history_200.csv
├── structured_customer_report.py
├── structured_customer_actions.json
└── README.md
```

The CrewAI source files and any dependency files should also remain in the project. The list above highlights known files and is not necessarily the complete directory structure.

Do not upload `.env` or `.venv/` to GitHub.

## Potential Business Applications

The underlying architecture can be adapted for:

- Customer segmentation and follow-up prioritization.
- E-commerce customer-retention workflows.
- Re-engagement campaigns for inactive customers.
- Customer-growth recommendation pipelines.
- CRM synchronization and spreadsheet-based operational workflows.

Actual integrations, business rules, and customer data requirements must be adapted for each client.

## Limitations and Future Improvements

- Validate recommendations against real business outcomes before using them in production.
- Add monitoring and alerting for failed workflow executions.
- Independently verify retry behavior and recovery from transient failures.
- Add automated tests and stronger input validation.
- Integrate the workflow with a client's CRM and business systems as required.
- Apply appropriate access controls and data-protection practices before processing real customer data.

## Portfolio Note

This project demonstrates practical experience combining multi-agent orchestration, Python, APIs, workflow automation, and CRM-style data synchronization.

It is a demonstration project using fictional customer data. Business results and improvements in retention or revenue have not been established by this demonstration.
