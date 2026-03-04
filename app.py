import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="Startup Analysis")
df = pd.read_csv("startup_cleaned.csv")
df["Date"] =pd.to_datetime(df["Date"],errors="coerce")
df["month"]=df["Date"].dt.month
df["Year"]=df["Date"].dt.year

# st.dataframe(df)
df["Investors"] = df["Investors"].fillna("Undisclosed")
def load_overall_analysis():
    st.title("Overall Analysis")

    #total invested amount
    total = round(df["Amount"].sum())
    max_funding = df.groupby("Startup")["Amount"].max().sort_values(ascending=False).head(1).values[0]
    avg_funding = df.groupby("Startup")["Amount"].sum().mean()
    nums_startups = df["Startup"].nunique()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total",str(total)+ "Cr")
    with col2:
        st.metric("Max Funding",str(max_funding) + "Cr")
    with col3:
        st.metric("Average Funding",str(round(avg_funding)) + "Cr")
    with col4:
        st.metric("Number of Startups",(nums_startups))
    st.header("MoM Graph")
    selected_option = st.selectbox("Select Type",["Total","Count"])
    if selected_option == "Total":
        temp_df = df.groupby(["Year", "month"])["Amount"].sum().reset_index()
    else:
        temp_df =  df.groupby(["Year", "month"])["Amount"].count().reset_index()
    temp_df["x_axis"] = temp_df["month"].astype("str") + "-" +temp_df["Year"].astype("str")
    fig5, ax5 = plt.subplots()
    ax5.plot(temp_df["x_axis"], temp_df["Amount"])
    st.pyplot(fig5)

def load_investor_details(investors):
    st.title(investors)
    # LOAD LAST 5 RECENT INVESTMENTS OF THE INVESTOR
    last5_df = df[df["Investors"].str.contains(investors)].head()[["Date", "Startup", "Vertical", "City", "Round", "Amount"]]
    st.subheader("Most Recent Investments")
    st.dataframe(last5_df)
    # BIGGEST INVESTMENT
    # Row 1
    col1, col2 = st.columns(2)

    with col1:
        big_series = df[df["Investors"].str.contains(investors)].groupby("Startup")["Amount"].sum().sort_values(
            ascending=False).head(5)
        st.subheader("Biggest Investments")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(big_series.index, big_series.values)
        plt.xticks(rotation=90)
        st.pyplot(fig)

    with col2:
        vertical_series = df[df["Investors"].str.contains(investors)].groupby("Vertical")["Amount"].sum()
        st.subheader("Sector Wise Investments")
        fig1, ax1 = plt.subplots(figsize=(4, 4))
        ax1.legend(vertical_series.index, loc="upper left", bbox_to_anchor=(1, 1))
        ax1.pie(vertical_series, labels=vertical_series.index)
        st.pyplot(fig1)

    # Row 2
    col3, col4 = st.columns(2)

    with col3:
        subvertical_series = df[df["Investors"].str.contains(investors)].groupby("SubVertical")["Amount"].sum()
        st.subheader("Sub-Vertical Investments")
        fig2, ax2 = plt.subplots(figsize=(4, 4))
        ax2.legend(subvertical_series.index, loc="upper left", bbox_to_anchor=(1, 1))
        ax2.pie(subvertical_series, labels=subvertical_series.index)
        st.pyplot(fig2)

    with col4:
        city_series = df[df["Investors"].str.contains(investors)].groupby("City")["Amount"].sum()
        st.subheader("City Wise Investments")
        fig3, ax3 = plt.subplots(figsize=(4, 4))
        ax3.legend(subvertical_series.index, loc="upper left", bbox_to_anchor=(1, 1))
        ax3.pie(city_series, labels=city_series.index)
        st.pyplot(fig3)

    df["Year"] = df["Date"].dt.year
    year_series = df[df["Investors"].str.contains(investors)].groupby("Year")["Amount"].sum()
    st.subheader("Year Wise Investments")
    fig4, ax4 = plt.subplots()
    ax4.plot(year_series.index, year_series.values)
    st.pyplot(fig4)

st.sidebar.title("Startup Funding Analysis")
option = st.sidebar.selectbox("Select one", ["Overall Analysis", "Startup", " Investors"])

if option == "Overall Analysis":
    load_overall_analysis()
#btn0 = st.sidebar.button("Find Overall Analysis")
   #if btn0:

elif option == "Startup":
    st.title("Startup Analysis")
    st.sidebar.selectbox("Select Startup", sorted(df["Startup"].unique().tolist()))
    btn1 = st.sidebar.button("Find Startup Details")
else:
    selected_investor = st.sidebar.selectbox("Select Investor", sorted(set(df["Investors"].str.split(',').sum())))
    btn2 = st.sidebar.button("Find Investor Details")
    if btn2:
        load_investor_details(selected_investor)

