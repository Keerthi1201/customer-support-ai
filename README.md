# Customer-Support-AI

##Overview

This project is an AI-powered support ticket analysis system built using Python, FastAPI, Pandas, and Ollama Llama 3.2. The application allows users to query customer support ticket data using natural language, detect anomalies in ticket records, and access insights through REST API endpoints.The LLM is used for understanding the user's natural-language question and converting it into a structured intent. The actual data processing, filtering, grouping, aggregation, and anomaly detection are handled using Python and Pandas.

--
##Features

- Natural language querying of support ticket data
- LLM-based intent understanding using Ollama
- Python/Pandas-based ticket analysis
- Automated anomaly detection
- REST API built with FastAPI
- Support for ticket analytics and operational insights
- Zero-cost local execution using Ollama

  ## System Architecture
  User Request
  │
  ▼
  FastAPI
  │
  ▼ Query Engine
  │
  ▼ Ollama Llama 3.2
  │
  ▼ Python/Pandas Logic
  │
  ▼ Support Ticket Dataset

  ## Project Structure
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

  Installation
1. Clone the Repository
git clone https://github.com/Eshwar1210/customer-support-ai.git
cd customer-support-ai
2. Create Virtual Environment
python -m venv venv
3. Install Dependencies
.\venv\Scripts\python.exe -m pip install -r requirements.txt
4. Install Ollama Model

Make sure Ollama is installed on your system.

Download the required local model:

ollama pull llama3.2:3b

Check whether the model is installed:

ollama list
Running the Application

Start the FastAPI server:

.\venv\Scripts\python.exe -m uvicorn app.main:app --reload

API documentation will be available at:

http://127.0.0.1:8000/docs
API Endpoints
Method	Endpoint	Description
GET	/health	Health check endpoint
POST	/query	Natural language query endpoint
GET	/anomalies	Detect anomalous tickets
Example Query
Request
{
  "question": "How many tickets are currently open?"
}
Response
{
  "question": "How many tickets are currently open?",
  "llm_interpreted_intent": {
    "action": "count_open_tickets",
    "category": null,
    "hours": null
  },
  "answer": "There are 42 open tickets.",
  "data": [
    {
      "open_tickets": 42
    }
  ]
}
Example Questions
How many tickets are currently open?
Which agent has the lowest average customer rating?
What is the average customer rating for Technical category tickets?
Show me Critical tickets not resolved within 12 hours.
Are there any anomalies in resolution times?
Anomaly Detection

The system detects the following anomaly types:

Tickets with unusually long resolution time.
High or Critical priority tickets that are unresolved for more than 24 hours.

Example anomaly response:

{
  "total_anomalies": 10,
  "resolution_time_threshold_hrs": 25.4,
  "anomalies": [
    {
      "ticket_id": "TKT-001",
      "priority": "Critical",
      "status": "Open",
      "anomaly_reason": "High/Critical unresolved ticket older than 24 hours"
    }
  ]
}
Design Decisions

FastAPI was chosen because it is lightweight, fast, and provides automatic API documentation through Swagger UI.

Pandas was used for efficient CSV loading, filtering, grouping, and analytics.

Ollama Llama 3.2 was selected because it allows free local LLM execution without using paid APIs.

The LLM is used only for natural language understanding. Python and Pandas perform the actual calculations to keep the output more reliable and explainable.

Known Limitations
The dataset is loaded into memory.
The system currently supports only the provided support ticket schema.
Anomaly detection is rule-based.
The LLM is used for intent classification, not open-ended conversation.
Unsupported or complex questions may return a general summary.
No authentication is implemented because this is a prototype.
Future Improvements
Add Streamlit chatbot-style UI
Add charts and visual dashboard
Add Docker support
Improve LLM intent classification
Add more anomaly detection rules
Add authentication and role-based access
Author

Eshwar Kotikalapudi

AI Engineer Assessment Submission
