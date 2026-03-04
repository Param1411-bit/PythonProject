import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Startup Intelligence Dashboard")

# -------------------------
# LOAD DATA
# -------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("startup_cleaned.csv")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month

    df["Investors"] = df["Investors"].fillna("Undisclosed")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    return df


df = load_data()


# -------------------------
# OVERALL ANALYSIS
# -------------------------

def load_overall_analysis():

    st.title("📊 Startup Funding Intelligence Dashboard")

    total_funding = round(df["Amount"].sum())
    max_funding = df.groupby("Startup")["Amount"].sum().max()
    avg_funding = df.groupby("Startup")["Amount"].sum().mean()
    total_startups = df["Startup"].nunique()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Total Funding", f"{total_funding} Cr")
    col2.metric("🚀 Max Startup Funding", f"{round(max_funding)} Cr")
    col3.metric("📈 Avg Startup Funding", f"{round(avg_funding)} Cr")
    col4.metric("🏢 Funded Startups", total_startups)

    st.divider()

    # -----------------------
    # MoM Funding Trend
    # -----------------------

    st.subheader("📈 Funding Trend")

    option = st.selectbox("Select Type", ["Total Funding", "Deal Count"])

    if option == "Total Funding":
        temp = df.groupby(["Year", "Month"])["Amount"].sum().reset_index()
    else:
        temp = df.groupby(["Year", "Month"])["Amount"].count().reset_index()

    temp["Date"] = pd.to_datetime(
        dict(year=temp["Year"], month=temp["Month"], day=1)
    )

    fig = px.line(
        temp,
        x="Date",
        y="Amount",
        markers=True,
        title="Monthly Funding Trend"
    )

    st.plotly_chart(fig,use_container_width=True)

    st.divider()

    col1,col2 = st.columns(2)

    with col1:

        st.subheader("🏭 Top Sectors")

        sector = df.groupby("Vertical")["Amount"].sum().sort_values(ascending=False).head(8)

        fig = px.pie(
            values=sector.values,
            names=sector.index,
            title="Sector Distribution"
        )

        st.plotly_chart(fig,use_container_width=True)

    with col2:

        st.subheader("🌆 City Wise Funding")

        city = df.groupby("City")["Amount"].sum().sort_values(ascending=False).head(10)

        fig = px.bar(
            x=city.index,
            y=city.values,
            title="Top Funding Cities"
        )

        st.plotly_chart(fig,use_container_width=True)

    st.divider()

    # -----------------------
    # Top Investors
    # -----------------------

    st.subheader("🏦 Top Investors")

    investors = df["Investors"].str.split(",").sum()
    investor_series = pd.Series(investors).value_counts().head(10)

    fig = px.bar(
        investor_series,
        orientation="h",
        title="Top Investors by Deal Count"
    )

    st.plotly_chart(fig,use_container_width=True)

    st.divider()

    # -----------------------
    # Funding Heatmap
    # -----------------------

    st.subheader("🔥 Funding Heatmap")

    heatmap = df.pivot_table(
        values="Amount",
        index="Vertical",
        columns="Year",
        aggfunc="sum"
    )

    fig = px.imshow(
        heatmap,
        aspect="auto",
        title="Sector vs Year Funding Heatmap"
    )

    st.plotly_chart(fig,use_container_width=True)



# -------------------------
# STARTUP ANALYSIS
# -------------------------

def load_startup_details(startup):

    st.title(f"🏢 {startup}")

    startup_df = df[df["Startup"]==startup]

    col1,col2,col3 = st.columns(3)

    col1.metric("Funding Rounds",startup_df.shape[0])
    col2.metric("Total Funding",round(startup_df["Amount"].sum()))
    col3.metric("Investors",startup_df["Investors"].nunique())

    st.divider()

    st.subheader("Funding History")

    st.dataframe(
        startup_df[["Date","Round","Investors","City","Amount"]]
    )

    st.divider()

    st.subheader("Similar Companies")

    vertical = startup_df["Vertical"].values[0]

    similar = df[df["Vertical"]==vertical]

    similar = similar[similar["Startup"]!=startup]

    st.dataframe(
        similar[["Startup","City","Amount","Investors"]].head(10)
    )



# -------------------------
# INVESTOR ANALYSIS
# -------------------------

def load_investor_details(investor):

    st.title(f"💼 {investor}")

    investor_df = df[df["Investors"].str.contains(investor)]

    st.subheader("Recent Investments")

    st.dataframe(
        investor_df.sort_values("Date",ascending=False).head(5)[
            ["Date","Startup","Vertical","City","Round","Amount"]
        ]
    )

    st.divider()

    col1,col2 = st.columns(2)

    with col1:

        st.subheader("Biggest Investments")

        big = investor_df.groupby("Startup")["Amount"].sum().sort_values(ascending=False).head(5)

        fig = px.bar(
            x=big.index,
            y=big.values
        )

        st.plotly_chart(fig,use_container_width=True)

    with col2:

        st.subheader("Sector Preference")

        sector = investor_df.groupby("Vertical")["Amount"].sum().sort_values(ascending=False).head(6)

        fig = px.pie(
            values=sector.values,
            names=sector.index
        )

        st.plotly_chart(fig,use_container_width=True)

    col3,col4 = st.columns(2)

    with col3:

        st.subheader("Stage Preference")

        stage = investor_df.groupby("Round")["Amount"].sum()

        fig = px.pie(
            values=stage.values,
            names=stage.index
        )

        st.plotly_chart(fig,use_container_width=True)

    with col4:

        st.subheader("City Preference")

        city = investor_df.groupby("City")["Amount"].sum()

        fig = px.pie(
            values=city.values,
            names=city.index
        )

        st.plotly_chart(fig,use_container_width=True)

    st.divider()

    st.subheader("Yearly Investment Trend")

    year = investor_df.groupby("Year")["Amount"].sum()

    fig = px.line(
        x=year.index,
        y=year.values,
        markers=True
    )

    st.plotly_chart(fig,use_container_width=True)

    st.divider()

    st.subheader("Similar Investors")

    sectors = investor_df["Vertical"].unique()

    similar = df[df["Vertical"].isin(sectors)]

    sim_inv = set(similar["Investors"].str.split(",").sum())

    sim_inv.discard(investor)

    st.write(list(sim_inv)[:10])



# -------------------------
# SIDEBAR NAVIGATION
# -------------------------

st.sidebar.title("Startup Intelligence Dashboard")

option = st.sidebar.selectbox(
    "Select View",
    ["Overall Analysis","Startup Analysis","Investor Analysis"]
)

# -------------------------

if option == "Overall Analysis":

    load_overall_analysis()

elif option == "Startup Analysis":

    startup = st.sidebar.selectbox(
        "Select Startup",
        sorted(df["Startup"].unique())
    )

    if st.sidebar.button("Analyze Startup"):

        load_startup_details(startup)

else:

    investor = st.sidebar.selectbox(
        "Select Investor",
        sorted(set(df["Investors"].str.split(",").sum()))
    )

    if st.sidebar.button("Analyze Investor"):

        load_investor_details(investor)