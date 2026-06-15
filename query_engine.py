import json
import re
from pathlib import Path

import pandas as pd
import requests


CSV_PATH = Path("data/support_tickets.csv")
XLSX_PATH = Path("data/support_tickets.xlsx")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"


def load_dataset():
    if CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
    elif XLSX_PATH.exists():
        df = pd.read_excel(XLSX_PATH)
    else:
        raise FileNotFoundError(
            "Dataset not found. Put support_tickets.csv inside the data folder."
        )

    df.columns = [
        col.strip().lower().replace(" ", "_")
        for col in df.columns
    ]

    rename_map = {
        "resp_time_hrs": "response_time_hrs",
        "resol_time_hrs": "resolution_time_hrs",
        "cust_rating": "customer_rating",
    }

    df = df.rename(columns=rename_map)

    required_columns = [
        "ticket_id",
        "created_at",
        "category",
        "priority",
        "status",
        "response_time_hrs",
        "resolution_time_hrs",
        "agent_id",
        "customer_rating",
        "issue_summary",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing columns in dataset: {missing_columns}")

    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["response_time_hrs"] = pd.to_numeric(df["response_time_hrs"], errors="coerce")
    df["resolution_time_hrs"] = pd.to_numeric(df["resolution_time_hrs"], errors="coerce")
    df["customer_rating"] = pd.to_numeric(df["customer_rating"], errors="coerce")

    return df


def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise ValueError("No JSON found in LLM response.")

    return json.loads(match.group())


def get_intent_from_llm(question):
    prompt = f"""
You are an AI assistant for customer support ticket analysis.

Understand the user's question and return JSON only.

Available actions:
1. count_open_tickets
2. count_unresolved_critical
3. lowest_avg_customer_rating_agent
4. most_resolved_agent_latest_month
5. critical_not_resolved_within_hours
6. avg_customer_rating_by_category
7. tickets_by_status
8. tickets_by_priority
9. anomalies
10. general_summary

Return JSON only in this format:
{{
  "action": "action_name",
  "category": null,
  "hours": null
}}

Rules:
- If question asks average rating for Technical/Billing/General, set category.
- If question asks not resolved within N hours, set hours as number.
- If unsure, use general_summary.

User question:
{question}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )

    response.raise_for_status()
    raw_response = response.json()["response"]

    return extract_json(raw_response)


def fallback_intent(question):
    q = question.lower()

    if "open" in q and "ticket" in q:
        return {"action": "count_open_tickets", "category": None, "hours": None}

    if "critical" in q and ("unresolved" in q or "not resolved" in q):
        hours_match = re.search(r"(\d+)\s*hour", q)
        hours = int(hours_match.group(1)) if hours_match else 24

        return {
            "action": "critical_not_resolved_within_hours",
            "category": None,
            "hours": hours
        }

    if "lowest" in q and "customer rating" in q:
        return {
            "action": "lowest_avg_customer_rating_agent",
            "category": None,
            "hours": None
        }

    if "resolved the most" in q or "most tickets" in q:
        return {
            "action": "most_resolved_agent_latest_month",
            "category": None,
            "hours": None
        }

    if "average customer rating" in q:
        category = None

        for possible_category in ["technical", "billing", "general"]:
            if possible_category in q:
                category = possible_category.capitalize()

        return {
            "action": "avg_customer_rating_by_category",
            "category": category,
            "hours": None
        }

    if "status" in q:
        return {"action": "tickets_by_status", "category": None, "hours": None}

    if "priority" in q:
        return {"action": "tickets_by_priority", "category": None, "hours": None}

    if "anomaly" in q or "anomalies" in q:
        return {"action": "anomalies", "category": None, "hours": None}

    return {"action": "general_summary", "category": None, "hours": None}


def safe_get_intent(question):
    try:
        return get_intent_from_llm(question)
    except Exception:
        return fallback_intent(question)


def records_to_json(df):
    output = df.copy()

    for column in output.columns:
        if pd.api.types.is_datetime64_any_dtype(output[column]):
            output[column] = output[column].astype(str)

    return output.fillna("").to_dict(orient="records")


def execute_intent(df, intent):
    action = intent.get("action")

    if action == "count_open_tickets":
        count = len(df[df["status"].str.lower() == "open"])

        return {
            "answer": f"There are {count} open tickets.",
            "data": [{"open_tickets": count}]
        }

    if action == "count_unresolved_critical":
        filtered = df[
            (df["priority"].str.lower() == "critical")
            & (df["status"].str.lower() != "resolved")
        ]

        return {
            "answer": f"There are {len(filtered)} unresolved critical tickets.",
            "data": records_to_json(filtered)
        }

    if action == "lowest_avg_customer_rating_agent":
        result = (
            df.dropna(subset=["customer_rating"])
            .groupby("agent_id")["customer_rating"]
            .mean()
            .reset_index(name="average_customer_rating")
            .sort_values("average_customer_rating", ascending=True)
            .head(1)
        )

        if result.empty:
            return {
                "answer": "No customer rating data is available.",
                "data": []
            }

        agent = result.iloc[0]["agent_id"]
        rating = round(result.iloc[0]["average_customer_rating"], 2)

        return {
            "answer": f"Agent {agent} has the lowest average customer rating: {rating}.",
            "data": records_to_json(result)
        }

    if action == "most_resolved_agent_latest_month":
        resolved = df[df["status"].str.lower() == "resolved"].copy()

        if resolved.empty:
            return {
                "answer": "No resolved tickets found.",
                "data": []
            }

        latest_month = resolved["created_at"].dt.to_period("M").max()
        latest_month_data = resolved[
            resolved["created_at"].dt.to_period("M") == latest_month
        ]

        result = (
            latest_month_data
            .groupby("agent_id")["ticket_id"]
            .count()
            .reset_index(name="resolved_ticket_count")
            .sort_values("resolved_ticket_count", ascending=False)
            .head(1)
        )

        if result.empty:
            return {
                "answer": "No resolved tickets found for the latest month.",
                "data": []
            }

        agent = result.iloc[0]["agent_id"]
        count = int(result.iloc[0]["resolved_ticket_count"])

        return {
            "answer": f"Agent {agent} resolved the most tickets in the latest month: {count}.",
            "data": records_to_json(result)
        }

    if action == "critical_not_resolved_within_hours":
        hours = intent.get("hours") or 12

        filtered = df[
            (df["priority"].str.lower() == "critical")
            & (
                (df["status"].str.lower() != "resolved")
                | (df["resolution_time_hrs"] > hours)
            )
        ]

        return {
            "answer": f"Found {len(filtered)} critical tickets not resolved within {hours} hours.",
            "data": records_to_json(filtered)
        }

    if action == "avg_customer_rating_by_category":
        category = intent.get("category")

        if category:
            filtered = df[
                df["category"].str.lower() == str(category).lower()
            ]

            avg_rating = filtered["customer_rating"].mean()

            if pd.isna(avg_rating):
                return {
                    "answer": f"No customer rating data found for {category} category.",
                    "data": []
                }

            return {
                "answer": f"The average customer rating for {category} tickets is {round(avg_rating, 2)}.",
                "data": [{
                    "category": category,
                    "average_customer_rating": round(avg_rating, 2)
                }]
            }

        result = (
            df.dropna(subset=["customer_rating"])
            .groupby("category")["customer_rating"]
            .mean()
            .reset_index(name="average_customer_rating")
        )

        return {
            "answer": "Average customer rating by category calculated successfully.",
            "data": records_to_json(result)
        }

    if action == "tickets_by_status":
        result = df["status"].value_counts().reset_index()
        result.columns = ["status", "ticket_count"]

        return {
            "answer": "Ticket count by status calculated successfully.",
            "data": records_to_json(result)
        }

    if action == "tickets_by_priority":
        result = df["priority"].value_counts().reset_index()
        result.columns = ["priority", "ticket_count"]

        return {
            "answer": "Ticket count by priority calculated successfully.",
            "data": records_to_json(result)
        }

    return general_summary(df)


def general_summary(df):
    total_tickets = len(df)
    open_tickets = len(df[df["status"].str.lower() == "open"])
    resolved_tickets = len(df[df["status"].str.lower() == "resolved"])
    escalated_tickets = len(df[df["status"].str.lower() == "escalated"])

    avg_response_time = df["response_time_hrs"].mean()
    avg_resolution_time = df["resolution_time_hrs"].mean()
    avg_customer_rating = df["customer_rating"].mean()

    return {
        "answer": "General ticket summary generated successfully.",
        "data": [{
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "resolved_tickets": resolved_tickets,
            "escalated_tickets": escalated_tickets,
            "average_response_time_hrs": round(avg_response_time, 2),
            "average_resolution_time_hrs": round(avg_resolution_time, 2),
            "average_customer_rating": round(avg_customer_rating, 2)
        }]
    }


def ask_question(question):
    df = load_dataset()
    intent = safe_get_intent(question)
    result = execute_intent(df, intent)

    return {
        "question": question,
        "llm_interpreted_intent": intent,
        "answer": result["answer"],
        "data": result["data"]
    }
