import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Bike Rental Dashboard", layout="wide")

def get_aggregated_df(df, groupby_col, agg_dict, mapping=None):
    new_df = df.groupby(groupby_col, observed=False).agg(agg_dict).reset_index()
    if mapping:
        new_df[groupby_col] = new_df[groupby_col].map(mapping)
    return new_df

@st.cache_data
def load_data():
    df = pd.read_csv("Dashboard/main_data.csv")
    df["dteday"] = pd.to_datetime(df["dteday"])
    df.sort_values(by="dteday", inplace=True)
    return df

all_df = load_data()
MIN_DATE, MAX_DATE = all_df["dteday"].min(), all_df["dteday"].max()

with st.sidebar:
    st.title("Dashboard 🚲")
    start_date = st.date_input("Min Date", MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE)
    end_date = st.date_input("Max Date", MAX_DATE, min_value=MIN_DATE, max_value=MAX_DATE)
    st.divider()


main_df = all_df[(all_df["dteday"] >= pd.Timestamp(start_date)) & 
                 (all_df["dteday"] <= pd.Timestamp(end_date))]


daily_orders_df = main_df.resample(rule='D', on='dteday').agg({"cnt": "sum"}).reset_index()

monthly_orders_df = get_aggregated_df(main_df, "mnth", {"cnt": "mean"}, 
    {i: month for i, month in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)})

weekly_orders_df = get_aggregated_df(main_df.groupby("dteday").agg({"cnt":"sum", "weekday":"first"}), "weekday", {"cnt": "mean"},
    {0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat"})

seasonal_df = get_aggregated_df(main_df, "season", {"cnt": "mean"}, {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"})

weather_df = get_aggregated_df(main_df, "weathersit", {"cnt": "mean"}, 
    {1: "Clear", 2: "Mist", 3: "Light Rain/Snow", 4: "Heavy Rain/Snow"})

st.header("Bike Rental Dashboard 🚲⛅")
st.subheader(f"Overview: {start_date} to {end_date}")

col1, col2, col3 = st.columns(3)
col1.metric("Total Bike Rental", f"{daily_orders_df.cnt.sum():,}")
col2.metric("Average per Day", f"{daily_orders_df.cnt.mean():,.2f}")
with col3:
    st.write(f"**Max:** {daily_orders_df.cnt.max():,}")
    st.write(f"**Min:** {daily_orders_df.cnt.min():,}")

fig, ax = plt.subplots(figsize=(16, 6))
ax.plot(daily_orders_df["dteday"], daily_orders_df["cnt"], marker='o', color="#2e8a7f", lw=2)
st.pyplot(fig)

st.divider()

st.subheader("Time-Based Analysis")
tabs = st.tabs(["by Month", "by Hour"])

def plot_bar(df, x, y, title):
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=df, x=x, y=y, palette="viridis", ax=ax)
    st.pyplot(fig)
    c1, c2 = st.columns(2)
    c1.metric("Min", f"{df[y].min():,.2f}")
    c2.metric("Max", f"{df[y].max():,.2f}")

with tabs[0]: plot_bar(monthly_orders_df, "mnth", "cnt", "Monthly")
with tabs[1]: 
    hourly_df = main_df.groupby("hr")["cnt"].mean().reset_index()
    plot_bar(hourly_df, "hr", "cnt", "Hourly")

st.divider()

st.subheader("Weather Conditions")
c_pie, c_desc = st.columns([2, 1])
with c_pie:
    fig, ax = plt.subplots()
    ax.pie(weather_df["cnt"], labels=["Clear", "Mist","Light Rain/Snow", "Heavy Rain/Snow"], autopct='%1.1f%%', startangle=90, colors=sns.color_palette("viridis", 4))
    st.pyplot(fig)

st.divider()
col_u, col_d = st.columns(2)

with col_d:
    st.subheader("Holiday vs Working Day")
    day_type = main_df.groupby("workingday")["cnt"].mean()
    fig, ax = plt.subplots()
    ax.pie(day_type, labels=["Holiday", "Working Day"], autopct='%1.1f%%', colors=sns.color_palette("viridis", 2))
    st.pyplot(fig)