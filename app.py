from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA_PATH = Path("data/sample/rent_observations_sample.csv")
UNIT_ORDER = ["Studio", "1 Bedroom", "2 Bedroom", "3 Bedroom+"]

st.set_page_config(page_title="Toronto Rent Heatmap Lab", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    frame = pd.read_csv(DATA_PATH)
    frame["average_rent"] = pd.to_numeric(frame["average_rent"], errors="coerce")
    frame["vacancy_rate"] = pd.to_numeric(frame["vacancy_rate"], errors="coerce")
    frame["unit_count"] = pd.to_numeric(frame["unit_count"], errors="coerce")
    frame["is_suppressed"] = frame["average_rent"].isna()
    frame["unit_type"] = pd.Categorical(frame["unit_type"], categories=UNIT_ORDER, ordered=True)
    return frame


def money(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"${value:,.0f}"


def percent(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.1f}%"


def filtered_frame(frame: pd.DataFrame, year: int, unit_type: str) -> pd.DataFrame:
    return frame[(frame["reference_year"] == year) & (frame["unit_type"] == unit_type)].copy()


rent = load_data()

st.title("Toronto Rent Heatmap Lab")
st.caption(
    "Interactive rental pressure map prototype using a Power BI-ready warehouse shape. "
    "Sample data is bundled for demonstration; the ETL can load official CMHC tables."
)

with st.sidebar:
    st.header("Filters")
    selected_year = st.selectbox("Year", sorted(rent["reference_year"].unique(), reverse=True))
    selected_unit = st.selectbox("Unit type", UNIT_ORDER, index=1)
    selected_group = st.multiselect(
        "Geography group",
        sorted(rent["geography_group"].dropna().unique()),
        default=sorted(rent["geography_group"].dropna().unique()),
    )
    st.divider()
    st.caption("Pipeline")
    st.code("CMHC -> Python ETL -> SQL -> Power BI", language="text")

view = filtered_frame(rent, int(selected_year), selected_unit)
if selected_group:
    view = view[view["geography_group"].isin(selected_group)]

valid = view.dropna(subset=["average_rent"])
prior = filtered_frame(rent, int(selected_year) - 1, selected_unit)
prior = prior[["geography_id", "average_rent"]].rename(columns={"average_rent": "prior_rent"})
view = view.merge(prior, on="geography_id", how="left")
view["rent_change"] = view["average_rent"] - view["prior_rent"]
view["rent_change_pct"] = view["rent_change"] / view["prior_rent"]

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.metric("Average rent", money(valid["average_rent"].mean() if not valid.empty else None))
with kpi2:
    st.metric("Highest area", valid.loc[valid["average_rent"].idxmax(), "geography_name"] if not valid.empty else "N/A")
with kpi3:
    st.metric("Lowest area", valid.loc[valid["average_rent"].idxmin(), "geography_name"] if not valid.empty else "N/A")
with kpi4:
    st.metric("Avg. vacancy", percent(valid["vacancy_rate"].mean() if not valid.empty else None))
with kpi5:
    st.metric("Suppressed cells", int(view["is_suppressed"].sum()))

map_tab, ranking_tab, trend_tab, data_tab = st.tabs(["Rent heatmap", "Ranking", "Trend", "Data model"])

with map_tab:
    left, right = st.columns([1.35, 0.65])
    with left:
        if valid.empty:
            st.warning("No reportable rent values for this filter.")
        else:
            fig = px.scatter_map(
                valid,
                lat="latitude",
                lon="longitude",
                color="average_rent",
                size="unit_count",
                hover_name="geography_name",
                hover_data={
                    "average_rent": ":$,.0f",
                    "vacancy_rate": ":.1f",
                    "unit_count": ":,.0f",
                    "latitude": False,
                    "longitude": False,
                },
                color_continuous_scale=["#d9ead3", "#f1c232", "#cc4125"],
                size_max=44,
                zoom=12,
                height=610,
            )
            fig.update_layout(
                map_style="open-street-map",
                margin=dict(l=0, r=0, t=0, b=0),
                coloraxis_colorbar=dict(title="Avg rent"),
            )
            st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Selected layer")
        st.write(
            {
                "year": int(selected_year),
                "unit_type": selected_unit,
                "geographies": int(len(view)),
                "reportable_cells": int(len(valid)),
            }
        )
        st.subheader("Map interpretation")
        st.markdown(
            "Darker red areas indicate higher observed average rent. Circle size reflects the rental unit count in the sample model. Suppressed cells stay visible in the data table but are excluded from color scaling."
        )

with ranking_tab:
    ranking = valid.sort_values("average_rent", ascending=False)
    chart = px.bar(
        ranking,
        x="average_rent",
        y="geography_name",
        orientation="h",
        color="average_rent",
        color_continuous_scale=["#d9ead3", "#f1c232", "#cc4125"],
        labels={"average_rent": "Average rent", "geography_name": "Area"},
        height=430,
    )
    chart.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(chart, use_container_width=True)

    table = ranking[
        ["geography_name", "average_rent", "vacancy_rate", "unit_count", "rent_change", "rent_change_pct"]
    ].copy()
    table.columns = ["Area", "Average rent", "Vacancy rate", "Rental units", "YoY change $", "YoY change %"]
    st.dataframe(table, use_container_width=True, hide_index=True)

with trend_tab:
    trend = rent.dropna(subset=["average_rent"])
    trend = trend[trend["unit_type"] == selected_unit]
    line = px.line(
        trend,
        x="reference_year",
        y="average_rent",
        color="geography_name",
        markers=True,
        labels={"reference_year": "Year", "average_rent": "Average rent", "geography_name": "Area"},
        height=430,
    )
    line.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(line, use_container_width=True)

    matrix = rent[rent["reference_year"] == selected_year].pivot_table(
        index="geography_name",
        columns="unit_type",
        values="average_rent",
        observed=False,
    )
    heat = go.Figure(
        data=go.Heatmap(
            z=matrix.values,
            x=list(matrix.columns.astype(str)),
            y=list(matrix.index),
            colorscale=[[0, "#d9ead3"], [0.5, "#f1c232"], [1, "#cc4125"]],
            colorbar=dict(title="Avg rent"),
        )
    )
    heat.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(heat, use_container_width=True)

with data_tab:
    st.subheader("Power BI-ready grain")
    st.code("one row per reference_year + geography_id + unit_type", language="text")
    st.dataframe(view.sort_values(["geography_name", "unit_type"]), use_container_width=True, hide_index=True)

    st.subheader("Next data upgrade")
    st.markdown(
        "The current deployed app uses bundled sample rows so the dashboard can be viewed immediately. "
        "The repository ETL supports loading official CMHC wide or normalized tables, then exporting the same model to Power BI."
    )
