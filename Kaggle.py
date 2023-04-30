import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

@st.cache()
def load_data():
    df = pd.read_csv(r'kaggle_survey_2017_2021.csv', sep=',',skiprows=1)
    df['survey_id'] = df.index
    
    ################
    ### Cleaning ###
    ################

    df = df.rename(columns={'What is the highest level of formal education that you have attained or plan to attain within the next 2 years?': 'Education'})
    df["Education"] = df["Education"].str.replace('Bachelorâ€™s degree', 'Bachelor\'s degree', regex=False)
    df["Education"] = df["Education"].str.replace('Masterâ€™s degree', 'Master\'s degree', regex=False)

    ################
    ### Cleaning ###
    ################

    df = df.rename(columns={'For how many years have you been writing code and/or programming?': 'Coding_Years'})
    df["Coding_Years"] = df["Coding_Years"].str.replace('1 to 2 years', '1-3 years', regex=False)
    df["Coding_Years"] = df["Coding_Years"].str.replace('1-2 years', '1-3 years', regex=False)
    df["Coding_Years"] = df["Coding_Years"].str.replace('< 1 years', '< 1 year', regex=False)
    df["Coding_Years"] = df["Coding_Years"].str.replace('3 to 5 years', '3-5 years', regex=False)
    df["Coding_Years"] = df["Coding_Years"].str.replace('Less than a year', '< 1 year', regex=False)

    df["Coding_Years"] = df["Coding_Years"].str.replace('6 to 10 years', '6-10 years', regex=False)

    df["Coding_Years"] = df["Coding_Years"].str.replace('10-20 years', 'More than 10 years', regex=False)
    df["Coding_Years"] = df["Coding_Years"].str.replace('20-30 years', 'More than 10 years', regex=False)
    df["Coding_Years"] = df["Coding_Years"].str.replace('30-40 years', 'More than 10 years', regex=False)
    df["Coding_Years"] = df["Coding_Years"].str.replace('20+ years', 'More than 10 years', regex=False)
    df["Coding_Years"] = df["Coding_Years"].str.replace('40+ years', 'More than 10 years', regex=False)

    df["Coding_Years"] = df["Coding_Years"].str.replace('I don\'t write code to analyze data', '0', regex=False)
    df["Coding_Years"] = df["Coding_Years"].str.replace('I have never written code and I do not want to learn', '0', regex=False)
    df["Coding_Years"] = df["Coding_Years"].str.replace('I have never written code but I want to learn', '0', regex=False)
    df["Coding_Years"] = df["Coding_Years"].str.replace('I have never written code', '0', regex=False)
    
    
    df = df.rename(columns={'Select the title most similar to your current role (or most recent title if retired): - Selected Choice': 'Job_Title'})
    
    return (df)

df = load_data()

#################  
### Add State ###   
#################
if 'df' not in st.session_state:
    st.session_state.df=df

##############
### Filter ###   
##############
    
year_list = df['Year'].dropna().sort_values(ascending=True).unique()

with st.sidebar:
    with st.expander('Year'):
        all_year = st.checkbox("Select All Years",key='year_checkbox')
        year_container = st.container()

        if all_year:
            selected_year = year_container.multiselect("Select Year",year_list,year_list)
        else:
            selected_year =  year_container.multiselect("Select Year",year_list)
            
            
job_list = df['Job_Title'].dropna().sort_values(ascending=True).unique()

with st.sidebar:
    with st.expander('Job'):
        all_job = st.checkbox("Select All Jobs",key='job_checkbox')
        job_container = st.container()

        if all_job:
            selected_job = job_container.multiselect("Select Job",job_list,job_list)
        else:
            selected_job =  job_container.multiselect("Select Job",job_list)
    
########################
### DF after Filters ###
########################

st.session_state['df'] = df[(df.Year.isin(selected_year))&
                            (df.Job_Title.isin(selected_job))
                           ]

###########
### KPI ###
###########

col1,col2,col3,col4 = st.columns(4)

with col1:
    participants = st.session_state['df']['survey_id'].nunique()
    participants_kpi = f'{participants:,.0f}'
    st.metric(label='Participants', value=participants_kpi)

with col2:
    python = st.session_state['df']['What programming languages do you use on a regular basis? (Select all that apply) - Selected Choice - Python'].notnull().sum()
    python_percentage = python/participants*100
    python_kpi = f'{python_percentage:,.1f}%'
    st.metric(label='Python Users', value=python_kpi)

with col3:
    R = st.session_state['df']['What programming languages do you use on a regular basis? (Select all that apply) - Selected Choice - R'].notnull().sum()
    R_percentage = R/participants*100
    R_kpi = f'{R_percentage:,.1f}%'
    st.metric(label='R Users', value=R_kpi)

with col4:
    SQL = st.session_state['df']['What programming languages do you use on a regular basis? (Select all that apply) - Selected Choice - SQL'].notnull().sum()
    SQL_percentage = SQL/participants*100
    SQL_kpi = f'{SQL_percentage:,.1f}%'
    st.metric(label='SQL Users', value=SQL_kpi)
    
col1,col2 = st.columns(2)

###############
### Chart 1 ###
###############
with col1:
    df2 = st.session_state['df'].groupby(['Job_Title']).agg(survey_id_size=('survey_id', 'size')).reset_index()

    # Step: Sort column(s) survey_id_size descending (Z-A)
    df2 = df2.sort_values(by=['survey_id_size'], ascending=[False])

    fig = px.bar(df2, y='survey_id_size', x='Job_Title',title='Job Title', height=600)
    fig

###############
### Chart 2 ###
###############

with col2:
    fig = px.histogram(st.session_state['df'].dropna(subset=['What is your age (# years)?']), x='What is your age (# years)?',title='Age Distribution of Survey Participants', height=600
                       # ,facet_col='Year',category_orders={"Year": [2017, 2018, 2019, 2020,2021]}
                      )
    fig.update_xaxes(categoryorder='category ascending')
    fig

###############
### Chart 3 ###
###############

with col1:
    df3 = st.session_state['df'].groupby(['Job_Title', 'Education']).agg(Count=('survey_id', 'size')).reset_index()
    df3 = df3.sort_values(by=['Count'], ascending=[False])
    fig = px.treemap(df3, path=['Job_Title', 'Education'], values='Count', height=600,title='Highest Qualification')
    fig


###############
### Chart 4 ###
###############
with col2:
    df4 = st.session_state['df'].groupby(['Job_Title', 'Coding_Years']).agg(Count=('survey_id', 'size')).reset_index()
    df4 = df4.sort_values(by=['Count'], ascending=[False])

    fig = px.treemap(df4, path=['Job_Title', 'Coding_Years'], values='Count', height=600,title='Coding Experience')
    fig


###############
### Chart 5 ###
###############
with col1:
    df5 = st.session_state['df'].groupby(['Year','What programming language would you recommend an aspiring data scientist to learn first? - Selected Choice']).agg(Count=('survey_id', 'size')).reset_index()
    df5['Year'] = df5['Year'].astype('string')
    fig = px.bar(df5, x='What programming language would you recommend an aspiring data scientist to learn first? - Selected Choice', y='Count',
                 color='Year', barmode='group',
                 height=600,title='Recommended Programming Language')
    fig.update_xaxes(categoryorder='total descending')
    fig

###############
### Chart 6 ###
###############
with col2:
    df6 = st.session_state['df'].groupby(['Year','Which of the following business intelligence tools do you use most often? - Selected Choice']).agg(Count=('survey_id', 'size')).reset_index()
    df6['Year'] = df6['Year'].astype('string')
    fig = px.bar(df6, x='Which of the following business intelligence tools do you use most often? - Selected Choice', y='Count',
                 color='Year', barmode='group',
                 height=600,title='Recommended BI tool')
    fig.update_xaxes(categoryorder='total descending')
    fig

