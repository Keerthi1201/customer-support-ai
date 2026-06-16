# AI-Powered Support Ticket Analysis System


## Overview

This project is an AI-powered customer support ticket analysis system built using Python, FastAPI, Pandas, and Ollama Llama 3.2.The application allows users to analyze customer support ticket data using natural language questions, detect anomalous ticket records, and access ticket insights through REST API endpoints.The LLM is used for understanding the user’s question and converting it into a structured intent. The actual data filtering, grouping, calculations, and anomaly detection are handled using Python and Pandas.

---

--
##Features

- Natural language querying of support ticket data
- LLM-based intent understanding using Ollama Llama 3.2
- Customer support ticket analytics using Pandas
- REST API built with FastAPI
- Automated anomaly detection
- Detect unresolved high-priority and critical tickets
- Detect tickets with unusually long resolution times
- Generate structured JSON API responses
- Local execution without paid API keys

  ---

## Tech Stack

- Python
- FastAPI
- Pandas
- Pydantic
- Requests
- Ollama
- Llama 3.2 3B
- Uvicorn
- CSV / Excel Dataset

---

## System Architecture

```text
User Request
     |
     v
FastAPI API
     |
     v
Query Engine
     |
     v
Ollama Llama 3.2
     |
     v
Python / Pandas Logic
     |
     v
Support Ticket Dataset
     |
     v
JSON Response
```

 ## Project Structure
 ```text
  customer-support-ai/
  │
  ├── app/
  │ └── main.py
  │
  ├── data/
  │ └── support_tickets.csv
  ├── query_engine.py
  ├── anomaly.py
  ├── requirements.txt
  ├── README.md
  └── .gitignore
```
## Dataset Columns
The support ticket dataset contains the following columns:
* ticket_id
* created_at
* category
* priority
* status
* response_time_hrs
* resolution_time_hrs
* agent_id
* customer_rating
* issue_summary

## Installation

1. Clone the Repository
```bash
cd "C:\Users\nagin\OneDrive\Desktop\customer-support-ai"
```

2. Create Virtual Environment
```bash
python -m venv venv
```

3. Activate Virtual Environment
```bash
.\venv\Scripts\activate
```
4. Install Dependencies
```bash
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```
5. Run the Application
```bash
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

 ## Install Ollama Model

Make sure Ollama is installed on your system.Download the required local model:

```bash
ollama pull llama3.2:3b
```

Check whether the model is installed:

```bash
ollama list
```

Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

API documentation will be available at:


```bash
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint   | Description                     |
| ------ | ---------- | ------------------------------- |
| GET    | /health    | Health check endpoint           |
| POST   | /query     | Natural language query endpoint |
| GET    | /anomalies | Detect anomalous tickets        |

---

## Example Query

### Request

```json
{
  "question": "How many tickets are currently open?"
}
```

### Response

```json
{
  "answer": "The dataset contains 42 open tickets."
}
```

---

## Design Decisions

* FastAPI was chosen for its simplicity, performance, and automatic API documentation.
* Pandas was used for efficient data loading and analysis.
* Groq Llama 3 was selected to enable natural language interaction with ticket data.

---

## Known Limitations

* Dataset is loaded into memory.
* Anomaly detection is rule-based.
* Query accuracy depends on LLM responses.

---

## Author

AI Engineer Assessment Submission
