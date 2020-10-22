import streamlit as st
import pandas as pd
import altair as alt

######################### global tables ########################

explanations = { "Total"        :"Total number of people with major",
                "Men"           :"Male graduates",
                "Women"         :"Female graduates",
                "Employed"      :"Number of employed",
                "Full_time"     :"Employed 35 hours or more",
                "Part_time"     :"Employed less than 35 hours",
                "Full_time_year_round":"Employed at least 50 weeks and at least 35 hours",
                "Unemployed"    :"Number of unemployed",
                "Unemployment_rate":"Unemployed / (Unemployed + Employed)",
                "Median"        :"Median earnings of full-time, year-round workers",
                "P25th"         :"25th percentile of earnings",
                "P75th"         :"75th percentile of earnings",
                "College_jobs"  :"Number with job requiring a college degree",
                "Non_college_jobs":"Number with job not requiring a college degree",
                "Low_wage_jobs" :"Number in low-wage service jobs"
                }
rev_explanations = { v : k for k, v in explanations.items() }

##################### end of global tables #####################

####################### helper functions #######################
@st.cache  # add caching so we load the data only once
def load_data():
    recent_grad_url = "https://raw.githubusercontent.com/fivethirtyeight/data/master/college-majors/recent-grads.csv"
    return pd.read_csv(recent_grad_url)

def draw_title():
    st.markdown(
    """
        # Lets's analyze some data about College Majors!

        Made by Shaobo Guan (shaobog) and Yuxi Luo (yuxiluo)
        - Github repository: [Group a3-lol](https://github.com/CMU-IDS-2020/a3-lol)

        ## Project Overview

        Nowadays students have a wide range of majors that they can pursue as a college student. However, will every college majors ensure similar economic standing after graduation? We want to investigate into the relationship between college majors and their corresponding economic status. The dataset [College Majors](https://github.com/fivethirtyeight/data/blob/master/college-majors/recent-grads.csv) we chose contains information about a total of 173 college majors, including various statistics to quantitatively describe a major from an economic perspective. For example, it contains median earnings for each majors. The statistics allow us to understand college majors and the corresponding economic income after graduation.

        In particular, as students of the School of Computer Science at Carnegie Mellon University, we want to figure out whether our major is the most profitable major among all of the 173 college majors :)

        Several other interesting questions can be investigated while playing around with the tool we built:

        - Are STEM majors more profitable than other majors?
        - Are there less women in STEM majors?
        - Do any of two statistics have some correlations between each other?
    """
    )

def draw_selection(selection):
    selected = st.sidebar.multiselect('Choose some major categories!', selection, default=selection)
    return selected

def draw_major_statistics(df, selected, useful_cols):
    # first visualization #
    st.header("Let's explore various statistics of all majors!")
    filtered_df = df.loc[df["Major_category"].isin(selected)]

    # select box #
    option_field = rev_explanations[st.selectbox('Choose a field!', useful_cols)]

    avg_brush = alt.selection(type='interval', encodings=['y'])

    chart = alt.Chart(filtered_df).mark_bar().encode(
        x=alt.X(option_field, scale=alt.Scale(zero=False),),
        y=alt.Y("Major", scale=alt.Scale(zero=False),
                sort = '-x',
                axis=alt.Axis(labelOverlap=True)),
        color=alt.Y("Major_category"),
        opacity=alt.condition(avg_brush, alt.OpacityValue(1), alt.OpacityValue(0.4)),
        tooltip=["Major", "Major_category", option_field]
    ).add_selection(
        avg_brush
    ).properties(
        width=1000, height=750
    )

    avg_line = alt.Chart(filtered_df).mark_rule(color='firebrick').encode(
        x='mean(' + option_field + '):Q',
        size=alt.SizeValue(3)
    ).transform_filter(
        avg_brush
    ).properties(
        width=1000, height=750
    )

    visual_1 = alt.layer(chart, avg_line)

    st.write(visual_1)
    # first visualization end #

def draw_correlations(df, selected, useful_cols):
    # second visualization #
    st.header("Try to see some correlations and distributions between two statistics of your choice!")
    filtered_df = df.loc[df["Major_category"].isin(selected)]

    # select box #
    option_field_x = rev_explanations[st.selectbox('Choose a field for the x-axis!', useful_cols)]
    option_field_y = rev_explanations[st.selectbox('Choose a field for the y-axis!', useful_cols)]

    brush = alt.selection(type = 'interval')

    corr = alt.Chart(filtered_df).mark_point().encode(
        x=alt.X(option_field_x+":Q",
                scale=alt.Scale(zero=False),
                axis=alt.Axis(labelOverlap=True),
                ),
        y=alt.Y(option_field_y+":Q",
                scale=alt.Scale(zero=False),
                axis=alt.Axis(labelOverlap=True),
                ),
        opacity=alt.condition(brush, alt.OpacityValue(1), alt.OpacityValue(0.1)),
        color=alt.Y("Major_category"),
        tooltip=["Major", option_field_y, option_field_x]
    ).add_selection(
        brush
    ).properties(
        width=1000, height=400
    )

    support_chart = alt.Chart(filtered_df).mark_bar().encode(
        x=alt.X("Major", scale=alt.Scale(zero=False),
                sort = '-y',
                axis=alt.Axis(labelOverlap=True)),
        color=alt.condition(brush,
                            alt.Color('Major_category:N', legend=None),
                            alt.value('lightgray')),
        tooltip=["Major", "Major_category"],
    ).properties(
        width=400, height=300
    )

    visual_2 = corr & \
        (support_chart.encode(y=alt.Y(option_field_x, scale=alt.Scale(zero=False))) | \
        support_chart.encode(y=alt.Y(option_field_y, scale=alt.Scale(zero=False))))


    st.write(visual_2)
    # second visualization end #

####################### end of helper functions #######################
df = load_data()
categories = df["Major_category"].unique()
useful_cols = [explanations[df.columns[i]] for i in range(len(df.columns)) \
                if df.columns[i] not in ['Rank', 'Major_code', 'Major', \
                'Major_category', 'Sample_size', 'ShareWomen']]

draw_title()
selected = draw_selection(list(categories))
draw_major_statistics(df, selected, useful_cols)
draw_correlations(df, selected, useful_cols)
