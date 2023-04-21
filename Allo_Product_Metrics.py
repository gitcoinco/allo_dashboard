import streamlit as st
import os
import pandas as pd
from pandas.io.json import json_normalize
import json
import numpy as np
import requests
import datetime
import locale
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

path = 'Allo_Product_Dashboard-ac51c10481ae.json'

st.set_page_config(layout="wide")

# Variables
chain_id = 1
round_address = "0xD95A1969c41112cEE9A2c931E849bCef36a16F4C"

# filter function
def df_filter(message,df):
        slider_1, slider_2 = st.slider('%s' % (message),0,len(df)-1,[0,len(df)-1],1)

        while len(str(df.iloc[slider_1][1]).replace('.0','')) < 4:
            df.iloc[slider_1,1] = '0' + str(df.iloc[slider_1][1]).replace('.0','')
            
        while len(str(df.iloc[slider_2][1]).replace('.0','')) < 4:
            df.iloc[slider_2,1] = '0' + str(df.iloc[slider_1][1]).replace('.0','')

        start_date = datetime.datetime.strptime(str(df.iloc[slider_1][0]).replace('.0','') + str(df.iloc[slider_1][1]).replace('.0',''),'%Y-%m-%d %H:%M:%S%f')
        start_date = start_date.strftime('%d %b %Y, %I:%M%p')
        
        end_date = datetime.datetime.strptime(str(df.iloc[slider_2][0]).replace('.0','') + str(df.iloc[slider_2][1]).replace('.0',''),'%Y-%m-%d %H:%M:%S%f')
        end_date = end_date.strftime('%d %b %Y, %I:%M%p')

        st.info('Start: **%s**    End: **%s**' % (start_date,end_date))
        
        filtered_df = df.iloc[slider_1:slider_2+1][:].reset_index(drop=True)

        return filtered_df

# def df_filter(message,df):
#         slider_1, slider_2 = st.slider('%s' % (message),0,len(df)-1,[0,len(df)-1],1)

#         while len(str(df.iloc[slider_1][1]).replace('.0','')) < 4:
#             df.iloc[slider_1,1] = '0' + str(df.iloc[slider_1][1]).replace('.0','')
            
#         while len(str(df.iloc[slider_2][1]).replace('.0','')) < 4:
#             df.iloc[slider_2,1] = '0' + str(df.iloc[slider_1][1]).replace('.0','')

#         start_date = datetime.datetime.strptime(str(df.iloc[slider_1][0]).replace('.0','') + str(df.iloc[slider_1][1]).replace('.0',''),'%Y-%m-%d %H:%M:%S%f')
#         start_date = start_date.strftime('%d %b %Y, %I:%M%p')
        
#         end_date = datetime.datetime.strptime(str(df.iloc[slider_2][0]).replace('.0','') + str(df.iloc[slider_2][1]).replace('.0',''),'%Y-%m-%d %H:%M:%S%f')
#         end_date = end_date.strftime('%d %b %Y, %I:%M%p')

#         st.info('Start: **%s**    End: **%s**' % (start_date,end_date))
        
#         filtered_df = df.iloc[slider_1:slider_2+1][:].reset_index(drop=True)

#         return filtered_df

siteHeader = st.container()

with siteHeader:
  st.title('Allo Product Metrics')
  st.text('In this report, we''ll take a deep dive analysis of general and usage specific metrics for Allo.')

  st.title('Round Overview')
  # Rounds
  round_url = f"https://grants-stack-indexer.fly.dev/data/{chain_id}/rounds.json"
  round_response = requests.request("GET", round_url)
  round_json = round_response.json()
  round_df = pd.json_normalize(round_json)
  round_df['applicationsStartTime'] = pd.to_datetime(round_df['applicationsStartTime'].astype(int),unit='s')
  round_df['applicationsEndTime'] = pd.to_datetime(round_df['applicationsEndTime'].astype(int),unit='s')
  round_df['roundStartTime'] = pd.to_datetime(round_df['roundStartTime'].astype(int),unit='s')
  round_df['roundEndTime'] = pd.to_datetime(round_df['roundEndTime'].astype(int),unit='s')
  round_df['applicationMetadata.lastUpdatedOn'] = round_df['applicationMetadata.lastUpdatedOn'].fillna(0)
  round_df['applicationMetadata.lastUpdatedOn'] = pd.to_datetime(round_df['applicationMetadata.lastUpdatedOn'].astype(int)/1000,unit='s')

  # filtered_df = df_filter('Move slider to filter data',round_df)

  new_round_records = round_df.loc[round_df['applicationMetadata.lastUpdatedOn'] >= pd.Timestamp.today().normalize()] 

  col1, col2, col3 = st.columns(3)
  col1.metric("QF Round", str(len(round_df.index)), f"{len(new_round_records.index)} from yesterday")
  col2.metric("QV Rounds", "N/A", "0 from yesterday")
  col3.metric("Direct Grant Rounds", "N/A", "0 from yesterday")

  locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

  col1.metric("$ Total Distribution", str(locale.currency(round_df.loc[:, 'amountUSD'].sum().round(2), grouping = True)))
  col2.metric("Avg Total Distribution", str(locale.currency(round_df.loc[:, 'amountUSD'].mean().round(2), grouping = True)))
  col3.metric("Total Unique Contributors",str(round_df.loc[:, 'uniqueContributors'].sum()))
  
  st.title('Project Overview')

  # Projects
  tot_projects_url = f"https://grants-stack-indexer.fly.dev/data/{chain_id}/projects.json"
  tot_proj_response = requests.request("GET", tot_projects_url)
  tot_proj_json = tot_proj_response.json()
  tot_project_df = pd.json_normalize(tot_proj_json)

  print(tot_project_df.keys())
  tot_project_df['metadata.createdAt'] = tot_project_df['metadata.createdAt'].fillna(0)
  tot_project_df['metadata.createdAt'] = pd.to_datetime(tot_project_df['metadata.createdAt'].astype(int)/1000,unit='s')

  new_projects = tot_project_df.loc[tot_project_df['metadata.createdAt'] >= pd.Timestamp.today().normalize()] 

  # Round details
  filtered_round_data = round_df.loc[round_df['roundStartTime'] >= '2023-04-25 00:00:00']

  r_round = []
  r_projects = []
  r_name = []
  # accepted_projects = []
  # rejected_projects = []
  # no_decsision_projects = []
  p_data = pd.DataFrame()
  v_data = pd.DataFrame()

  for ind in filtered_round_data.index:

    r_round.append(filtered_round_data['id'][ind])
    r_name.append(filtered_round_data["metadata.name"][ind])

    r_projects_url = f"https://grants-stack-indexer.fly.dev/data/{chain_id}/rounds/{filtered_round_data['id'][ind]}/projects.json"

    proj_response = requests.request("GET", r_projects_url)
    proj_json = proj_response.json()
    projects_df = pd.json_normalize(proj_json)

    votes_url = f"https://grants-stack-indexer.fly.dev/data/{chain_id}/rounds/{filtered_round_data['id'][ind]}/votes.json"
    votes_response = requests.request("GET", votes_url)
    votes_json = votes_response.json()
    votes_df = pd.json_normalize(votes_json)

    r_projects.append(len(projects_df.index))
    p_data = p_data.append(projects_df, ignore_index=True)
    v_data = v_data.append(votes_df, ignore_index=True)
    # accepted_projects.append(projects_df.loc[df['International'] == 'N', 'Student_ID'].nunique())
    # rejected_projects.append(projects_df.loc[df['International'] == 'N', 'Student_ID'].nunique())
    # no_decsision_projects.append()

  beta_round_dataset = pd.DataFrame(list(zip(r_round, r_name, r_projects)), columns =['Round ID', 'Round name', 'Total projects'])
  p_data['metadata.application.project.createdAt'] = p_data['metadata.application.project.createdAt'].fillna(0)
  p_data['metadata.application.project.createdAt'] = pd.to_datetime(p_data['metadata.application.project.createdAt'].astype(int)/1000,unit='s')
  
  new_round_projects = p_data.loc[p_data['metadata.application.project.createdAt'] >= pd.Timestamp.today().normalize()] 
  
  col1_oc, col2_oc, col3_oc = st.columns(3)
  col1_oc.metric("Total Projects", str(len(tot_project_df.index)), f"{len(new_round_records.index)} from yesterday")
  col2_oc.metric("Projects in Current Round", str(p_data['metadata.application.project.id'].nunique()), f"{new_round_projects['metadata.application.project.id'].nunique()} from yesterday")
  col3_oc.metric("Total Votes", "N/A", "0 from yesterday")

  st.subheader('Projects by Current Round')

  # style
  th_props = [
    ('font-size', '14px'),
    ('text-align', 'center'),
    ('font-weight', 'bold'),
    ('color', '#6d6d6d'),
    ('background-color', '#f7ffff')
    ]
                                
  td_props = [
    ('font-size', '12px')
    ]
                                  
  styles = [
    dict(selector="th", props=th_props),
    dict(selector="td", props=td_props)
    ]

  # table
  table_df = beta_round_dataset[['Round name', 'Total projects']].style.set_properties(**{'text-align': 'left'}).set_table_styles(styles)
  st.table(table_df)
  # # Contributors
  # contributors_url = f"https://grants-stack-indexer.fly.dev/data/{chain_id}/rounds/{round_address}/contributors.json"
  # con_response = requests.request("GET", contributors_url)
  # con_json = con_response.json()
  # contributors_df = pd.json_normalize(con_json)

  # # Votes
  # votes_url = f"https://grants-stack-indexer.fly.dev/data/{chain_id}/rounds/{round_address}/votes.json"
  # vote_response = requests.request("GET", votes_url)
  # vote_json = vote_response.json()
  # vote_df = pd.json_normalize(vote_json)


  st.title('App Usage')
  tab1, tab2, tab3 = st.tabs(["Explorer", "Manager", "Builder"])

  with tab1:
    property_id = st.secrets["e_property_id"]
    client = BetaAnalyticsDataClient.from_service_account_info(json.loads(st.secrets["google"]))

    request = RunReportRequest(
    property=f"properties/{property_id}",
    dimensions=[Dimension(name="date")],
    metrics=[Metric(name="activeUsers"), Metric(name="newUsers"), Metric(name="scrolledUsers"), Metric(name="userEngagementDuration"), Metric(name="wauPerMau"), Metric(name="sessions"), Metric(name="sessionsPerUser"), Metric(name='averageSessionDuration'), Metric(name='engagedSessions')],
    date_ranges=[DateRange(start_date="2020-03-31", end_date="today")],
    )
    explorer_response = client.run_report(request)

    date = []
    active_users = []
    new_users = []
    scrolled_users = []
    eng_duration = []
    wau_per_mau = []
    sessions = []
    sessions_per_user = []

    for row in explorer_response.rows:
        date.append(row.dimension_values[0].value)
        active_users.append(int(row.metric_values[0].value))
        new_users.append(int(row.metric_values[1].value))
        scrolled_users.append(int(row.metric_values[2].value))
        eng_duration.append(int(row.metric_values[3].value))
        wau_per_mau.append(float(row.metric_values[4].value))
        sessions.append(float(row.metric_values[5].value))
        sessions_per_user.append(float(row.metric_values[6].value))

    zipped_list = list(zip(date, active_users, new_users, scrolled_users, eng_duration, wau_per_mau, sessions, sessions_per_user))

    df = pd.DataFrame(zipped_list, columns=['date', 'active_users', 'new_users', 'scrolled_users', 'eng_duration', 'wau_per_mau', 'sessions', 'sessions_per_user']).sort_values(by=['date'], ascending=False)

    df[['date']] =  df[['date']].apply(pd.to_datetime)

    filtered_analytics = df_filter('Datetime Filter (Move slider to filter)', df)
    col_1, col_2 = st.columns(2)

    with col_1:
      st.header('New users')
      st.line_chart(filtered_analytics, x = 'date', y = 'new_users')

      st.header('Active users')
      st.line_chart(filtered_analytics, x = 'date', y = 'active_users')

    with col_2:
      st.header('Duration of engagement')
      st.bar_chart(filtered_analytics, x = 'date', y = 'eng_duration')

  # with tab2:
    # property_id = st.secrets["m_property_id"]
    # client = BetaAnalyticsDataClient.from_service_account_info(json.loads(st.secrets["google_man"]))

    # manager_request = RunReportRequest(
    # property=f"properties/{property_id}",
    # dimensions=[Dimension(name="date")],
    # metrics=[Metric(name="activeUsers"), Metric(name="newUsers"), Metric(name="scrolledUsers"), Metric(name="userEngagementDuration"), Metric(name="wauPerMau"), Metric(name="sessions"), Metric(name="sessionsPerUser"), Metric(name='averageSessionDuration'), Metric(name='engagedSessions')],
    # date_ranges=[DateRange(start_date="2020-03-31", end_date="today")],
    # )
    # manager_response = client.run_report(manager_request)

    # m_date = []
    # m_active_users = []
    # m_new_users = []
    # m_scrolled_users = []
    # m_eng_duration = []
    # m_wau_per_mau = []
    # m_sessions = []
    # m_sessions_per_user = []

    # for row in manager_response.rows:
    #     m_date.append(row.dimension_values[0].value)
    #     m_active_users.append(int(row.metric_values[0].value))
    #     m_new_users.append(int(row.metric_values[1].value))
    #     m_scrolled_users.append(int(row.metric_values[2].value))
    #     m_eng_duration.append(int(row.metric_values[3].value))
    #     m_wau_per_mau.append(float(row.metric_values[4].value))
    #     m_sessions.append(float(row.metric_values[5].value))
    #     m_sessions_per_user.append(float(row.metric_values[6].value))

    # m_zipped_list = list(zip(m_date, m_active_users, m_new_users, m_scrolled_users, m_eng_duration, m_wau_per_mau, m_sessions, m_sessions_per_user))

    # m_df = pd.DataFrame(m_zipped_list, columns=['date', 'active_users', 'new_users', 'scrolled_users', 'eng_duration', 'wau_per_mau', 'sessions', 'sessions_per_user']).sort_values(by=['date'], ascending=False)

    # m_df[['date']] =  m_df[['date']].apply(pd.to_datetime)
    # print(m_df.head())

    # m_filtered_analytics = df_filter('Datetime Filter (Move slider to filter)', m_df)
    # m_col_1, m_col_2 = st.columns(2)

    # with m_col_1:
    #   st.header('New users')
    #   st.line_chart(m_filtered_analytics, x = 'date', y = 'new_users')

    #   st.header('Active users')
    #   st.line_chart(m_filtered_analytics, x = 'date', y = 'active_users')

    # with m_col_2:
    #   st.header('Duration of engagement')
    #   st.bar_chart(m_filtered_analytics, x = 'date', y = 'eng_duration')

  with tab3:
    property_id = st.secrets["b_property_id"]
    client = BetaAnalyticsDataClient.from_service_account_info(json.loads(st.secrets["google_man"]))
    
    builder_request = RunReportRequest(
    property=f"properties/{property_id}",
    dimensions=[Dimension(name="date")],
    metrics=[Metric(name="activeUsers"), Metric(name="newUsers"), Metric(name="scrolledUsers"), Metric(name="userEngagementDuration"), Metric(name="wauPerMau"), Metric(name="sessions"), Metric(name="sessionsPerUser"), Metric(name='averageSessionDuration'), Metric(name='engagedSessions')],
    date_ranges=[DateRange(start_date="2020-03-31", end_date="today")],
    )
    builder_response = client.run_report(builder_request)

    b_date = []
    b_active_users = []
    b_new_users = []
    b_scrolled_users = []
    b_eng_duration = []
    b_wau_per_mau = []
    b_sessions = []
    b_sessions_per_user = []

    for row in builder_response.rows:
        b_date.append(row.dimension_values[0].value)
        b_active_users.append(int(row.metric_values[0].value))
        b_new_users.append(int(row.metric_values[1].value))
        b_scrolled_users.append(int(row.metric_values[2].value))
        b_eng_duration.append(int(row.metric_values[3].value))
        b_wau_per_mau.append(float(row.metric_values[4].value))
        b_sessions.append(float(row.metric_values[5].value))
        b_sessions_per_user.append(float(row.metric_values[6].value))

    b_zipped_list = list(zip(b_date, b_active_users, b_new_users, b_scrolled_users, b_eng_duration, b_wau_per_mau, b_sessions, b_sessions_per_user))

    b_df = pd.DataFrame(b_zipped_list, columns=['date', 'active_users', 'new_users', 'scrolled_users', 'eng_duration', 'wau_per_mau', 'sessions', 'sessions_per_user']).sort_values(by=['date'], ascending=False)

    b_df[['date']] =  b_df[['date']].apply(pd.to_datetime) 

    # b_filtered_analytics = df_filter('Datetime Filter (Move slider to filter)', b_df)
    b_col_1, b_col_2 = st.columns(2)

    with b_col_1:
      st.header('New users')
      st.line_chart(b_df, x = 'date', y = 'new_users')

      st.header('Active users')
      st.line_chart(b_df, x = 'date', y = 'active_users')

    with b_col_2:
      st.header('Duration of engagement')
      st.bar_chart(b_df, x = 'date', y = 'eng_duration')



  
