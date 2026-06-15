import pandas as pd
from pathlib import Path


CSV_PATH = Path("data/support_tickets.csv")
XLSX_PATH = Path("data/support_tickets.xlsx")


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

    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["resolution_time_hrs"] = pd.to_numeric(df["resolution_time_hrs"], errors="coerce")

    return df


def records_to_json(df):
    output = df.copy()

    for column in output.columns:
        if pd.api.types.is_datetime64_any_dtype(output[column]):
            output[column] = output[column].astype(str)

    return output.fillna("").to_dict(orient="records")


def detect_anomalies():
    df = load_dataset()

    resolved = df[df["resolution_time_hrs"].notna()]

    mean_resolution = resolved["resolution_time_hrs"].mean()
    std_resolution = resolved["resolution_time_hrs"].std()

    threshold = mean_resolution + (2 * std_resolution)

    long_resolution = df[
        df["resolution_time_hrs"].notna()
        & (df["resolution_time_hrs"] > threshold)
    ].copy()

    latest_time = df["created_at"].max()

    unresolved_high_priority = df[
        (df["status"].str.lower() != "resolved")
        & (df["priority"].str.lower().isin(["high", "critical"]))
        & ((latest_time - df["created_at"]).dt.total_seconds() / 3600 > 24)
    ].copy()

    long_resolution["anomaly_reason"] = "Abnormally long resolution time"
    unresolved_high_priority["anomaly_reason"] = "High/Critical unresolved ticket older than 24 hours"

    result = pd.concat(
        [long_resolution, unresolved_high_priority],
        ignore_index=True
    )

    return {
        "total_anomalies": len(result),
        "resolution_time_threshold_hrs": round(threshold, 2) if pd.notna(threshold) else None,
        "anomalies": records_to_json(result)
    }
