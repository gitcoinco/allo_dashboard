import streamlit as st
import os
import pandas as pd
from pandas.io.json import json_normalize
import json
import numpy as np
import altair as alt
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

def df_filter_2(message,df):
        slider_3, slider_4 = st.slider('%s' % (message),0,len(df)-1,[0,len(df)-1],2)

        while len(str(df.iloc[slider_3][1]).replace('.0','')) < 4:
            df.iloc[slider_3,1] = '0' + str(df.iloc[slider_3][1]).replace('.0','')
            
        while len(str(df.iloc[slider_4][1]).replace('.0','')) < 4:
            df.iloc[slider_4,1] = '0' + str(df.iloc[slider_3][1]).replace('.0','')

        start_date = datetime.datetime.strptime(str(df.iloc[slider_3][0]).replace('.0','') + str(df.iloc[slider_3][1]).replace('.0',''),'%Y-%m-%d %H:%M:%S%f')
        start_date = start_date.strftime('%d %b %Y, %I:%M%p')
        
        end_date = datetime.datetime.strptime(str(df.iloc[slider_4][0]).replace('.0','') + str(df.iloc[slider_4][1]).replace('.0',''),'%Y-%m-%d %H:%M:%S%f')
        end_date = end_date.strftime('%d %b %Y, %I:%M%p')

        st.info('Start: **%s**    End: **%s**' % (start_date,end_date))
        
        filtered_df = df.iloc[slider_3:slider_4+1][:].reset_index(drop=True)

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

@st.cache_data
def load_data(url):
  response = requests.request("GET", url)
  json = response.json()
  df = pd.json_normalize(json)
  return df

@st.cache_data 
def load_json_data(url):
  response = requests.request("GET", url)
  json = response.json()
  return json

@st.cache_data  # 👈 Add the caching decorator
def load_google_data(property_id, google_secret,_metrics, _dates):
  client = BetaAnalyticsDataClient.from_service_account_info(json.loads(google_secret))
  request = RunReportRequest(
    property=f"properties/{property_id}",
    dimensions=[Dimension(name="date")],
    metrics=_metrics,
    date_ranges=_dates
    )
  response = client.run_report(request)
  return response

siteHeader = st.container()

with siteHeader:
  st.title('Allo Product Metrics')
  st.text('In this report, we''ll take a deep dive analysis of general and usage specific metrics for Allo.')

  st.title('Round Overview')
  # Rounds
  round_url = f"https://grants-stack-indexer.fly.dev/data/{chain_id}/rounds.json"
  round_df = load_data(round_url)
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
  pd.options.display.float_format = '{:,.2f}'.format
  col3.metric("Total Unique Contributors",str(round_df.loc[:, 'uniqueContributors'].sum()))
  
  st.title('Project Overview')

  # Projects
  tot_projects_url = f"https://grants-stack-indexer.fly.dev/data/{chain_id}/projects.json"
  tot_project_df = load_data(tot_projects_url)

  tot_project_df['metadata.createdAt'] = tot_project_df['metadata.createdAt'].fillna(0)
  tot_project_df['metadata.createdAt'] = pd.to_datetime(tot_project_df['metadata.createdAt'].astype(int)/1000,unit='s')

  tot_proj = tot_project_df.loc[tot_project_df['metadata.createdAt'] >= '2023-04-01 00:00:00'] 

  new_projects = tot_proj.loc[tot_proj['metadata.createdAt'] >= pd.Timestamp.today().normalize()] 

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
  a_data = pd.DataFrame()

  for ind in filtered_round_data.index:

    r_round.append(filtered_round_data['id'][ind])
    r_name.append(filtered_round_data["metadata.name"][ind])

    r_projects_url = f"https://grants-stack-indexer.fly.dev/data/{chain_id}/rounds/{filtered_round_data['id'][ind]}/projects.json"
    projects_df = load_data(r_projects_url)

    r_projects.append(len(projects_df.index))
    p_data = p_data.append(projects_df, ignore_index=True)

    
    r_app_url = f"https://grants-stack-indexer.fly.dev/data/{chain_id}/rounds/{filtered_round_data['id'][ind]}/applications.json"
    app_df = load_data(r_app_url)

    a_data = a_data.append(app_df, ignore_index=True)

    votes_url = f"https://grants-stack-indexer.fly.dev/data/{chain_id}/rounds/{filtered_round_data['id'][ind]}/votes.json"

    try:
      votes_df = load_data(votes_url)
      v_data = v_data.append(votes_df, ignore_index=True)

    except:
      continue

    # accepted_projects.append(projects_df.loc[df['International'] == 'N', 'Student_ID'].nunique())
    # rejected_projects.append(projects_df.loc[df['International'] == 'N', 'Student_ID'].nunique())
    # no_decsision_projects.append()

   # Get timestamp using block number
  initial_block = a_data['createdAtBlock'].min()

  eth_url = f"https://api.etherscan.io/api?module=block&action=getblockreward&blockno={initial_block}&apikey={st.secrets['eth_api']}"
  eth_json = load_json_data(eth_url)

  block_time = eth_json['result']['timeStamp']

  app_timestamps = []
  for i in a_data['createdAtBlock']:
    app_timestamps.append(int(block_time) + ( int(i) - int(initial_block))*12)

  status_timestamps = []
  for i in a_data['statusUpdatedAtBlock']:
    status_timestamps.append(int(block_time) + ( int(i) - int(initial_block))*12)

  a_data['createdAt'] = app_timestamps
  a_data['statusUpdated'] = status_timestamps

  vote_timestamps = []
  for i in v_data['blockNumber']:
    vote_timestamps.append(int(block_time) + ( int(i) - int(initial_block))*12)

  v_data['createdAt'] = vote_timestamps

  beta_round_dataset = pd.DataFrame(list(zip(r_round, r_name, r_projects)), columns =['Round ID', 'Round name', 'Total projects'])
  p_data['metadata.application.project.createdAt'] = p_data['metadata.application.project.createdAt'].fillna(0)
  p_data['metadata.application.project.createdAt'] = pd.to_datetime(p_data['metadata.application.project.createdAt'].astype(int)/1000,unit='s')
  a_data['createdAt'] = pd.to_datetime(a_data['createdAt'].astype(int),unit='s')
  a_data['statusUpdated'] = pd.to_datetime(a_data['statusUpdated'].astype(int),unit='s')
  v_data['createdAt'] = pd.to_datetime(v_data['createdAt'].astype(int),unit='s')

  a_data['reviewTime'] = (a_data['statusUpdated'] - a_data['createdAt']) / np.timedelta64(1, 'D')
  
  new_round_projects = p_data.loc[p_data['metadata.application.project.createdAt'] >= pd.Timestamp.today().normalize()] 
  new_app_projects = a_data.loc[a_data['createdAt'] >= pd.Timestamp.today().normalize()] 
  app_accepted = a_data.loc[a_data["status"].isin(['APPROVED'])] 
  new_app_accepted = a_data.loc[(a_data['createdAt'] >= pd.Timestamp.today().normalize()) & (a_data["status"].isin(['APPROVED']))] 
  new_votes = v_data.loc[v_data['createdAt'] >= pd.Timestamp.today().normalize()] 
  
  print(a_data.keys())
  col1_oc, col2_oc, col3_oc, col4_oc = st.columns(4)
  col1_oc.metric("Total Projects", str(len(tot_proj.index)), f"{len(new_round_records.index)} from yesterday")
  col2_oc.metric("All unique applications submitted after Apr 12th", str(a_data['projectNumber'].nunique()), f"{new_app_projects['projectNumber'].nunique()} from yesterday")
  col3_oc.metric("Accepted Applications", str(app_accepted['projectNumber'].nunique()), f"{new_app_accepted['projectNumber'].nunique()} from yesterday")
  col4_oc.metric("Avg Review Time (days)", str(a_data['reviewTime'].mean().round(1)))

  col1_oc.metric("Total Votes", str(v_data["id"].nunique()), f"{new_votes['id'].nunique()} from yesterday")
  col2_oc.metric("Total Unique Contributors", str(v_data['voter'].nunique()), f"{new_votes['voter'].nunique()} from yesterday")
  col3_oc.metric("Total Contribution", str(locale.currency(v_data['amountUSD'].sum().round(2), grouping = True)), str(locale.currency(v_data['amountUSD'].sum().round(2) - new_votes['amountUSD'].sum().round(2), grouping = True)) + " from yesterday")
  col4_oc.metric("Avg Contribution", str(locale.currency(round(v_data["amountUSD"].mean(),2), grouping = True)), str(locale.currency(round(v_data["amountUSD"].mean(),2) - round(new_votes['amountUSD'].mean(), 2), grouping = True)) + " from yesterday")

  p_count = p_data['metadata.application.project.createdAt'].value_counts().rename_axis('Creation date').reset_index(name='Projects')
  
  col_char1, col_char2 = st.columns(2)
  with col_char1:
    st.subheader('Project Creation')
    st.bar_chart(p_count, x = 'Creation date', y = 'Projects')

    # st.subheader('Avg Review Time by Project creation')
    # review_chart = alt.Chart(data=a_data).mark_bar().encode(
    #         x=alt.X("monthdate(createdAt):O", title='Project creation'),
    #         y=alt.Y("avg(reviewTime):Q"),
    #     )

    # st.altair_chart(review_chart, use_container_width=True)

  with col_char2:
    st.subheader("Votes in Current Round")

    chart = alt.Chart(data=v_data).mark_bar().encode(
            x=alt.X("monthdate(createdAt):O", title='Date'),
            y=alt.Y("count(id):Q"),
        )

    st.altair_chart(chart, use_container_width=True)
  # with col_char2:
  #   st.subheader('Votes over Time')
  #   st.bar_chart(v_data, x = 'createdAt', y = 'transaction')

  # with col_char2:
  #   st.subheader('Projects in the Beta Round')
  #   st.bar_chart(beta_round_dataset, y = 'Total projects', x = 'Round name')

  # # style
  # th_props = [
  #   ('font-size', '14px'),
  #   ('text-align', 'center'),
  #   ('font-weight', 'bold'),
  #   ('color', '#6d6d6d'),
  #   ('background-color', '#f7ffff')
  #   ]
                                
  # td_props = [
  #   ('font-size', '12px')
  #   ]
                                  
  # styles = [
  #   dict(selector="th", props=th_props),
  #   dict(selector="td", props=td_props)
  #   ]

  # # table
  # table_df = beta_round_dataset[['Round name', 'Total projects']].style.set_properties(**{'text-align': 'left'}).set_table_styles(styles)
  # st.table(table_df)
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
    google_secret = st.secrets["google"]
    metrics = [Metric(name="activeUsers"), Metric(name="newUsers"), Metric(name="scrolledUsers"), Metric(name="userEngagementDuration"), Metric(name="wauPerMau"), Metric(name="sessions"), Metric(name="sessionsPerUser"), Metric(name='averageSessionDuration'), Metric(name='engagedSessions')]
    dates = [DateRange(start_date="2020-03-31", end_date="today")]

    explorer_response = load_google_data(property_id, google_secret, metrics, dates)

    date = []
    device_category = []
    device_model = []
    active_users = []
    new_users = []
    scrolled_users = []
    eng_duration = []
    wau_per_mau = []
    sessions = []
    sessions_per_user = []
    avg_session_duration = []

    for row in explorer_response.rows:
        date.append(row.dimension_values[0].value)
        # device_category.append(row.dimension_values[1].value)
        # device_model.append(row.dimension_values[2].value)
        active_users.append(int(row.metric_values[0].value))
        new_users.append(int(row.metric_values[1].value))
        scrolled_users.append(int(row.metric_values[2].value))
        eng_duration.append(int(row.metric_values[3].value))
        wau_per_mau.append(float(row.metric_values[4].value))
        sessions.append(float(row.metric_values[5].value))
        sessions_per_user.append(float(row.metric_values[6].value))
        avg_session_duration.append(float(row.metric_values[7].value))

    zipped_list = list(zip(date, active_users, new_users, scrolled_users, eng_duration, wau_per_mau, sessions, sessions_per_user, avg_session_duration))

    df = pd.DataFrame(zipped_list, columns=['date','active_users','new_users', 'scrolled_users', 'eng_duration', 'wau_per_mau', 'sessions', 'sessions_per_user', 'avg_session_duration']).sort_values(by=['date'], ascending=False)

    df[['date']] =  df[['date']].apply(pd.to_datetime)

    # device_zipped_list = list(zip(device_category, device_model, active_users ))
    # device_df = df = pd.DataFrame(device_zipped_list, columns=['device_category', 'device_model', 'active_users'])

    # start_date, end_date = st.date_input('start date  - end date :', [])
    # if start_date < end_date:
    #     pass
    # else:
    #     st.error('Error: End date must fall after start date.')

    # (df['date'].dt.date > start_date) & (df['date'].dt.date <= end_date)

    cols1,_ = st.columns((1,2)) # To make it narrower
    with cols1:
      filtered_analytics = df_filter('Datetime Filter (Move slider to filter)', df)

    col_1, col_2 = st.columns(2)

    with col_1:
      st.header('New users')
      st.line_chart(filtered_analytics, x = 'date', y = 'new_users')

      st.header('Active users')
      st.line_chart(filtered_analytics, x = 'date', y = 'active_users')

    with col_2:
      st.header('Total sessions')
      st.line_chart(filtered_analytics, x = 'date', y = 'sessions')

      st.header('Avg session duration')
      st.bar_chart(filtered_analytics, x = 'date', y = 'avg_session_duration')

      # st.header('Devices Used')
      # st.bar_chart(device_df, x = 'device_category', y = 'active_users')
 

  with tab2:
    m_property_id = st.secrets["m_property_id"]
    m_google_secret = st.secrets["google_man_v2"]
    m_metrics=[Metric(name="activeUsers"), Metric(name="newUsers"), Metric(name="scrolledUsers"), Metric(name="userEngagementDuration"), Metric(name="wauPerMau"), Metric(name="sessions"), Metric(name="sessionsPerUser"), Metric(name='averageSessionDuration'), Metric(name='engagedSessions')]
    m_dates=[DateRange(start_date="2020-03-31", end_date="today")]

    manager_response = load_google_data(m_property_id, m_google_secret, m_metrics, m_dates)

    m_date = []
    m_active_users = []
    m_new_users = []
    m_scrolled_users = []
    m_eng_duration = []
    m_wau_per_mau = []
    m_sessions = []
    m_sessions_per_user = []
    m_device_category = []
    m_device_model = []
    m_avg_session_duration = []

    for row in manager_response.rows:
        m_date.append(row.dimension_values[0].value)
        m_active_users.append(int(row.metric_values[0].value))
        m_new_users.append(int(row.metric_values[1].value))
        m_scrolled_users.append(int(row.metric_values[2].value))
        m_eng_duration.append(int(row.metric_values[3].value))
        m_wau_per_mau.append(float(row.metric_values[4].value))
        m_sessions.append(float(row.metric_values[5].value))
        m_sessions_per_user.append(float(row.metric_values[6].value))
        m_avg_session_duration.append(float(row.metric_values[7].value))

    m_zipped_list = list(zip(m_date, m_active_users, m_new_users, m_scrolled_users, m_eng_duration, m_wau_per_mau, m_sessions, m_sessions_per_user, m_avg_session_duration))

    m_df = pd.DataFrame(m_zipped_list, columns=['date', 'active_users', 'new_users', 'scrolled_users', 'eng_duration', 'wau_per_mau', 'sessions', 'sessions_per_user', 'avg_session_duration']).sort_values(by=['date'], ascending=False)

    m_df[['date']] =  m_df[['date']].apply(pd.to_datetime)
    print(m_df.head())
    
    # m_col_1, m_col_2 = st.columns(2)

    # with m_col_1:
    #   st.header('New users')
    #   st.line_chart(m_filtered_analytics, x = 'date', y = 'new_users')

    #   st.header('Active users')
    #   st.line_chart(m_filtered_analytics, x = 'date', y = 'active_users')

    # with m_col_2:
    #   st.header('Duration of engagement')
    #   st.bar_chart(m_filtered_analytics, x = 'date', y = 'eng_duration')

    cols1,_ = st.columns((1,2)) # To make it narrower
    with cols1:
      m_filtered_analytics = df_filter_2('Datetime Filter (Move slider to filter)', m_df)

    col_1, col_2 = st.columns(2)

    with col_1:
      st.header('New users')
      st.line_chart(m_filtered_analytics, x = 'date', y = 'new_users')

      st.header('Active users')
      st.line_chart(m_filtered_analytics, x = 'date', y = 'active_users')

    with col_2:
      st.header('Total sessions')
      st.line_chart(m_filtered_analytics, x = 'date', y = 'sessions')

      st.header('Avg session duration')
      st.bar_chart(m_filtered_analytics, x = 'date', y = 'avg_session_duration')

  with tab3:
    b_property_id = st.secrets["b_property_id"]
    b_google_secret = st.secrets["google_man"]
    b_metrics=[Metric(name="activeUsers"), Metric(name="newUsers"), Metric(name="scrolledUsers"), Metric(name="userEngagementDuration"), Metric(name="wauPerMau"), Metric(name="sessions"), Metric(name="sessionsPerUser"), Metric(name='averageSessionDuration'), Metric(name='engagedSessions')]
    b_dates=[DateRange(start_date="2020-03-31", end_date="today")]

    builder_response = load_google_data(b_property_id, b_google_secret, b_metrics, b_dates)

    b_date = []
    b_device_category = []
    b_device_model = []
    b_active_users = []
    b_new_users = []
    b_scrolled_users = []
    b_eng_duration = []
    b_wau_per_mau = []
    b_sessions = []
    b_sessions_per_user = []
    b_avg_session_duration = []

    for row in builder_response.rows:
        b_date.append(row.dimension_values[0].value)
        # b_device_category.append(row.dimension_values[1].value)
        # b_device_model.append(row.dimension_values[2].value)
        b_active_users.append(int(row.metric_values[0].value))
        b_new_users.append(int(row.metric_values[1].value))
        b_scrolled_users.append(int(row.metric_values[2].value))
        b_eng_duration.append(int(row.metric_values[3].value))
        b_wau_per_mau.append(float(row.metric_values[4].value))
        b_sessions.append(float(row.metric_values[5].value))
        b_sessions_per_user.append(float(row.metric_values[6].value))
        b_avg_session_duration.append(float(row.metric_values[7].value))

    b_zipped_list = list(zip(b_date, b_active_users, b_new_users, b_scrolled_users, b_eng_duration, b_wau_per_mau, b_sessions, b_sessions_per_user, b_avg_session_duration))

    b_df = pd.DataFrame(b_zipped_list, columns=['date','active_users','new_users', 'scrolled_users', 'eng_duration', 'wau_per_mau', 'sessions', 'sessions_per_user', 'avg_session_duration']).sort_values(by=['date'], ascending=False)

    b_df[['date']] =  b_df[['date']].apply(pd.to_datetime)

    # device_zipped_list = list(zip(device_category, device_model, active_users ))
    # device_df = df = pd.DataFrame(device_zipped_list, columns=['device_category', 'device_model', 'active_users'])

    # start_date, end_date = st.date_input('start date  - end date :', [])
    # if start_date < end_date:
    #     pass
    # else:
    #     st.error('Error: End date must fall after start date.')

    # (df['date'].dt.date > start_date) & (df['date'].dt.date <= end_date)

    cols1,_ = st.columns((1,2)) # To make it narrower
    with cols1:
      b_filtered_analytics = df_filter_2('Datetime Filter (Move slider to filter)', b_df)

    col_1, col_2 = st.columns(2)

    with col_1:
      st.header('New users')
      st.line_chart(b_filtered_analytics, x = 'date', y = 'new_users')

      st.header('Active users')
      st.line_chart(b_filtered_analytics, x = 'date', y = 'active_users')

    with col_2:
      st.header('Total sessions')
      st.line_chart(b_filtered_analytics, x = 'date', y = 'sessions')

      st.header('Avg session duration')
      st.bar_chart(b_filtered_analytics, x = 'date', y = 'avg_session_duration')

      # st.header('Devices Used')
      # st.bar_chart(device_df, x = 'device_category', y = 'active_users')



  
