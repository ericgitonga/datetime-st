import pandas as pd

import streamlit as st
import streamlit_analytics

import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="darkgrid")
st.set_page_config(layout="wide")

df = pd.read_csv("dt_kiva.csv")

df["funded_time"] = pd.to_datetime(df["funded_time"])
df.set_index("funded_time",inplace=True)

df["year"] = df.index.year
df["month"] = df.index.month_name()
df["month_number"] = df.index.month
df["day"] = df.index.day
df["days_in_month"] = df.index.daysinmonth

year_aggregates = df.groupby("year")["funded_amount"].sum().sort_values(ascending=False).reset_index()

high_day_list = []
for year in list(df["year"].unique()):
    df_year = df.groupby(["year","month","month_number","day"])["funded_amount"].sum().reset_index()
    df_year = df_year[df_year["year"] == year][["year","month","day","funded_amount", "month_number"]]
    for month in list(df["month"].unique()):
        df_high_day = df_year[df_year["month"] == month]
        df_high_day = df_high_day[df_high_day["funded_amount"] == df_high_day["funded_amount"].max()]
        high_day_list.append(df_high_day)
df_high_day = pd.concat(high_day_list).reset_index(drop=True)
sorted_df_high_day = []
for year in list (df_high_day["year"].unique()):
    sorted_df_high_day.append(df_high_day[df_high_day["year"] == year].sort_values(by="month_number"))
df_high_day = pd.concat(sorted_df_high_day).reset_index(drop=True).drop("month_number","columns")

df_average = df.groupby(["year","month","month_number","days_in_month"])["funded_amount"].sum().reset_index()
df_average["monthly_average"] = round(df_average["funded_amount"] / df_average["days_in_month"],2)
sorted_df_average = []
for year in list(df_average["year"].unique()):
    sorted_df_average.append(df_average[df_average["year"] == year].sort_values(by="month_number"))
df_average = pd.concat(sorted_df_average).reset_index(drop=True).         drop(["month_number","days_in_month","funded_amount"],"columns")

#Seaborn Plot
fig, ax = plt.subplots()

data = year_aggregates
x = year_aggregates["year"]
y = year_aggregates["funded_amount"]
top = 1.6e8

plt.ylim(top=top)
plt.yticks([])

ax = sns.barplot(data=data, x=x, y=y, color="lightblue", estimator=sum)
ax.set(xlabel="Year", ylabel="Funded Amount")

for p in ax.patches:
    ax.annotate(format(p.get_height()/1e6, '.2f'), 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha = 'center', va = 'center', 
                   xytext = (0, 9), 
                   textcoords = 'offset points')

#Plotly plots
fig_highest_daily = px.bar(df_high_day, x="month", y="funded_amount", title="Highest Daily Funded Amount",
            hover_data=["day","year"], facet_col="year",
            labels={"funded_amount":"Funded Amount","month":""})
fig_monthly_average = px.bar(df_average, x="month", y="monthly_average", title="Monthly Average of Funded Amount",
            hover_data=["year"], facet_col="year",
            labels={"monthly_average":"Monthly Average","month":""})
    
with streamlit_analytics.track():
    #Displaying the elements
    tl_left, tl_center, tl_right = st.beta_columns((1,4,1))
    with tl_center:
        st.markdown("## Illustrating pandas.DatetimeIndex via Kiva Funding")
        st.dataframe(df.sample(10))
    
    left_column, center_column, right_column = st.beta_columns(3)
    center_column.markdown("### Annual Funded Amount in Millions")
    
    left_container, center_container, right_container = st.beta_columns((1,2,1))

    with center_container:
        st.pyplot(fig)

    st.plotly_chart(fig_highest_daily, use_container_width=True)
    st.plotly_chart(fig_monthly_average, use_container_width=True)
