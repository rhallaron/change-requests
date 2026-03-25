import streamlit as st
import altair as alt
import pandas as pd
from src.utils import get_dataframe, get_dataframe_grouped, filter_options
from typing import Dict, List, Any

st.button("Refresh Data", on_click=st.cache_data.clear)

@st.cache_data
def get_df():
    return get_dataframe()

df = get_df()

def multiselect_option(df: pd.DataFrame, label: str, column: str):
    options = st.multiselect(label=label, options=filter_options(df, column))
    if options:
        exploded = (
            df
            .assign(filter_column=df[column].fillna("None").str.split(r"\s*,\s*"))
            .explode("filter_column")
            .reset_index(drop=True)
        )
        rows = list(exploded[exploded["filter_column"].isin(options)]["Row ID"].unique())
        df = df[df["Row ID"].isin(rows)]
    return df

def date_option(df: pd.DataFrame, label: str, column: str, key: str):
    with st.expander(f"{label}"):
        date_start = pd.to_datetime(st.date_input(label="Start", value=None, key=f"{key}_start"))
        date_end = pd.to_datetime(st.date_input(label="End", value=None, key=f"{key}_end"))
        if date_start and date_end:
            df = df[pd.to_datetime(df[column]).between(date_start, date_end)]
        elif date_start:
            df = df[pd.to_datetime(df[column]) >= date_start]
        elif date_end:
            df = df[pd.to_datetime(df[column]) <= date_end]
        return df
    
with st.container():
    st.set_page_config(layout="wide", page_title="Change Requests")

    st.title("Change Requests Dashboard")

    with st.sidebar:
        st.header("Filters")

        df = multiselect_option(df, label="Assigned To", column="Assigned to")
        df = multiselect_option(df, label="ECO Number", column="ECO #")
        df = multiselect_option(df, label="Embedded Jira", column="Embedded Jira")
        df = multiselect_option(df, label="Mobile Jira", column="Mobile Jira")
        df = multiselect_option(df, label="Product Impacted", column="Product Impacted")
        df = multiselect_option(df, label="Project ID", column="Project ID")
        df = multiselect_option(df, label="Request ID", column="Request ID")
        df = multiselect_option(df, label="Request Prefix", column="Designator")
        df = date_option(df, label="Follow Up", column="Follow Up", key="follow_up")
        df = date_option(df, label="Target Availability", column="Target Availability", key="target_availability")

    bar_type_df = df.groupby("Issue Type").size().reset_index(name="count")
    bar_status_df = df.groupby("Issue Status").size().reset_index(name="count")

    tab1, tab2 = st.tabs(["Requests by Type", "Requests by Status"])

    with tab1:
        point_selector = alt.selection_point(fields=["Issue Type"], empty="none")
        chart = (
            alt.Chart(bar_type_df)
            .mark_bar()
            .encode(
                x=alt.X("Issue Type", title="Issue Type"),
                y=alt.Y("count", title="Issue Count"),
                tooltip=["Issue Type", "count"],
                fillOpacity=alt.condition(point_selector, alt.value(1), alt.value(0.3))
            )
            .add_params(point_selector)
        )
        event = st.altair_chart(chart, use_container_width=True, on_select="rerun")
        if event["selection"]["param_1"]:
            selected = []
            for i in event["selection"]["param_1"]:
                selected.append(i["Issue Type"])
            df = df[df["Issue Type"].isin(selected)]

    with tab2:
        point_selector = alt.selection_point(fields=["Issue Status"], empty="none")
        chart = (
            alt.Chart(bar_status_df)
            .mark_bar()
            .encode(
                x=alt.X("Issue Status", title="Issue Status"),
                y=alt.Y("count", title="Issue Count"),
                tooltip=["Issue Status", "count"],
                fillOpacity=alt.condition(point_selector, alt.value(1), alt.value(0.3))
            )
            .add_params(point_selector)
        )
        event = st.altair_chart(chart, use_container_width=True, on_select="rerun")
        if event["selection"]["param_1"]:
            selected = []
            for i in event["selection"]["param_1"]:
                selected.append(i["Issue Status"])
            df = df[df["Issue Status"].isin(selected)]

    st.dataframe(df)
