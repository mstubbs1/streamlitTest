"""
San Diego Medicare Plans 2026 — Streamlit Starter
Ready for Railway / Render / local use.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="SD Medicare Plans 2026",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------
# Load data
# -------------------------------------------------
@st.cache_data
def load_data():
    path = Path(__file__).parent / "2026_San_Diego_Medicare_Plans_CLEANED.xlsx"
    df = pd.read_excel(path, sheet_name="All Plans")
    # Ensure string columns stay readable
    for col in df.columns:
        df[col] = df[col].fillna("").astype(str)
    return df


df = load_data()

# -------------------------------------------------
# Sidebar filters
# -------------------------------------------------
st.sidebar.title("Filters")

# Search
search = st.sidebar.text_input("Search (plan name, code, notes…)", "")

# Carrier
carriers = sorted([c for c in df["Carrier"].unique() if c.strip()])
selected_carriers = st.sidebar.multiselect("Carrier", carriers, default=carriers)

# Plan Type
plan_types = sorted([t for t in df["Plan Type"].unique() if t.strip()])
selected_types = st.sidebar.multiselect("Plan Type", plan_types, default=plan_types)

# Premium bucket
def premium_bucket(val: str) -> str:
    v = val.lower()
    if v in ("$0", "0", "") or v.startswith("$0 with"):
        return "$0 Premium"
    if "rebate" in v or "credit" in v:
        return "Part B Rebate / Credit"
    return "Paid Premium"


df["_premium_bucket"] = df["Premium"].apply(premium_bucket)
buckets = ["$0 Premium", "Part B Rebate / Credit", "Paid Premium"]
selected_buckets = st.sidebar.multiselect("Premium", buckets, default=buckets)

# Flags filter
show_flagged_only = st.sidebar.checkbox("Only show Cancelled / Non-Commissionable / Crosswalk", value=False)

# Apply filters
filtered = df.copy()

if selected_carriers:
    filtered = filtered[filtered["Carrier"].isin(selected_carriers)]
if selected_types:
    filtered = filtered[filtered["Plan Type"].isin(selected_types)]
if selected_buckets:
    filtered = filtered[filtered["_premium_bucket"].isin(selected_buckets)]
if show_flagged_only:
    filtered = filtered[filtered["Flags"].str.strip() != ""]

if search.strip():
    q = search.strip().lower()
    mask = (
        filtered["Plan Name"].str.lower().str.contains(q, na=False)
        | filtered["Plan Code"].str.lower().str.contains(q, na=False)
        | filtered["Notes"].str.lower().str.contains(q, na=False)
        | filtered["Carrier"].str.lower().str.contains(q, na=False)
    )
    filtered = filtered[mask]

st.sidebar.markdown(f"**{len(filtered)}** plans match")

# -------------------------------------------------
# Main content
# -------------------------------------------------
st.title("San Diego Medicare Plans 2026")
st.caption("Cleaned comparison data for licensed agents. Always verify with official Summary of Benefits / EOC.")

# Key columns for the main table
display_cols = [
    "Carrier",
    "Plan Name",
    "Plan Code",
    "Plan Type",
    "Premium",
    "Maximum Out of Pocket",
    "Doctors Visit",
    "Specialist Visit",
    "Dental Max",
    "Hearing Aids",
    "Vision",
    "Transportation",
    "OTC Benefits",
    "Gym Membership",
    "Flags",
]

# Only keep columns that exist
display_cols = [c for c in display_cols if c in filtered.columns]

st.subheader("Plan list")
st.dataframe(
    filtered[display_cols],
    use_container_width=True,
    hide_index=True,
    height=420,
)

# -------------------------------------------------
# Side-by-side comparison
# -------------------------------------------------
st.divider()
st.subheader("Compare plans side-by-side")

# Build selectable labels
filtered = filtered.reset_index(drop=True)
options = [
    f"{row['Carrier']} — {row['Plan Name']} ({row['Plan Code']})"
    for _, row in filtered.iterrows()
]

selected_labels = st.multiselect(
    "Select 2–4 plans to compare",
    options=options,
    max_selections=4,
    help="Pick a few plans to see key benefits next to each other.",
)

if selected_labels:
    # Map labels back to rows
    compare_rows = []
    for label in selected_labels:
        idx = options.index(label)
        compare_rows.append(filtered.iloc[idx])

    compare_df = pd.DataFrame(compare_rows)

    # Benefits to show in comparison (transpose for side-by-side feel)
    benefit_cols = [
        "Carrier",
        "Plan Name",
        "Plan Code",
        "Plan Type",
        "Premium",
        "Maximum Out of Pocket",
        "Doctors Visit",
        "Specialist Visit",
        "Outpatient Surgery",
        "Hospital Stay",
        "Skilled Nursing Facility",
        "Emergency Room",
        "Urgent Care",
        "Dental Type",
        "Dental Max",
        "Hearing Aids",
        "Vision",
        "Transportation",
        "OTC Benefits",
        "Gym Membership",
        "Chiropractor",
        "Acupuncture",
        "Flags",
        "Notes",
    ]
    benefit_cols = [c for c in benefit_cols if c in compare_df.columns]

    # Make plan names the column headers
    side_by_side = compare_df[benefit_cols].set_index("Plan Name").T
    side_by_side.index.name = "Benefit"

    st.dataframe(
        side_by_side,
        use_container_width=True,
        height=560,
    )
else:
    st.info("Select 2–4 plans above to see a side-by-side comparison.")

# -------------------------------------------------
# Medical Groups
# -------------------------------------------------
st.divider()
st.subheader("Medical Groups")

@st.cache_data
def load_medical_groups():
    path = Path(__file__).parent / "2026_San_Diego_Medicare_Plans_CLEANED.xlsx"
    return pd.read_excel(path, sheet_name="Medical Groups")

try:
    mg = load_medical_groups()
    for col in mg.columns:
        mg[col] = mg[col].fillna("").astype(str)

    mg_carriers = sorted([c for c in mg["Carrier"].unique() if c.strip()])
    selected_mg_carriers = st.multiselect(
        "Filter Medical Groups by Carrier",
        mg_carriers,
        default=[],
        key="mg_carriers",
    )

    mg_search = st.text_input("Search medical group name", key="mg_search")

    mg_filtered = mg.copy()
    if selected_mg_carriers:
        mg_filtered = mg_filtered[mg_filtered["Carrier"].isin(selected_mg_carriers)]
    if mg_search.strip():
        q = mg_search.strip().lower()
        mg_filtered = mg_filtered[
            mg_filtered["Medical Group"].str.lower().str.contains(q, na=False)
        ]

    st.caption(f"{len(mg_filtered)} rows")
    st.dataframe(
        mg_filtered,
        use_container_width=True,
        hide_index=True,
        height=400,
    )
except Exception as e:
    st.warning(f"Medical Groups sheet could not be loaded: {e}")

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.divider()
st.caption(
    "For licensed insurance agents only. Data is compiled from public sources and may contain errors. "
    "Not affiliated with CMS, Medicare.gov, or any carrier. Always verify final benefits with official plan documents."
)
