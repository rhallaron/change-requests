import streamlit as st
import pandas as pd
import json, requests, os
from ast import literal_eval
from dotenv import load_dotenv

def get_dataframe():
    
    def get_json():
        load_dotenv()
        req = requests.get(
            f"https://api.smartsheet.com/2.0/sheets/{os.getenv("SHEET_ID")}/",
            headers = {"Authorization": f"Bearer {os.getenv("API_TOKEN")}"}
        )
        return req.json()

    def parse_obj(x):
        if isinstance(x, str):
            try:
                return json.loads(x)
            except Exception:
                try:
                    return literal_eval(x)
                except Exception:
                    return x
        return x

    df = pd.json_normalize(get_json()).astype(str)
    data = []

    for _, row in df.iterrows():
        cols = {}

        for c in parse_obj(row.get("columns", [])):
            if c.get("id"):
                cols[c.get("id")] = c.get("title")

        for r in parse_obj(row.get("rows", [])):
            rcols = {}
            if isinstance(r, dict):
                if r.get("cells"):
                    for c in r.get("cells", []):
                        if c.get("columnId") in cols:
                            rcols[cols[c.get("columnId")]] = c.get("displayValue", c.get("value"))
                rcols["Row ID"] = r.get("id")
                data.append(rcols)

    output_df = pd.DataFrame(data)
    output_df["Date Requested"] = pd.to_datetime(output_df["Date Requested"], errors="coerce").dt.strftime("%m/%d/%Y")
    output_df["Target Availability"] = pd.to_datetime(output_df["Target Availability"], errors="coerce").dt.strftime("%m/%d/%Y")
    output_df["Requested Due Date"] = pd.to_datetime(output_df["Requested Due Date"], errors="coerce").dt.strftime("%m/%d/%Y")
    output_df["runtime"] = pd.Timestamp("now")

    return output_df

def get_dataframe_grouped(df: pd.DataFrame, column: str):
    return df.groupby(column).size().reset_index(name="count")

def filter_options(df: pd.DataFrame, column: str):
    exploded = (
        df
        .assign(filter_column=df[column].fillna("None").str.split(r"\s*,\s*"))
        .explode("filter_column")
        .reset_index(drop=True)
    )["filter_column"].unique()
    return sorted(list(exploded))
