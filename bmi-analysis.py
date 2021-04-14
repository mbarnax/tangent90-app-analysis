# Libraries:-
# Data handling
import pandas as pd
import numpy as np

# Could look in to using SciPy as well
# Data visualisation
import matplotlib.pyplot as plt
import seaborn as sns

# Web app hosting
import streamlit as st
plt.style.use('seaborn')

SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


st.title('Analysis of BMI App data')
st.image('./bmi-logo.png')

st.write('''
Taking raw click data from the Tangent90 app in order to draw some actionable insights. Looking at anything that could drive business and produce increased revenue.

By Max Barnes.
''')


# Importing data from github repository
DATA_URL = 'https://raw.githubusercontent.com/mbarnax/tangent90-app-analysis/main/bmi-data.csv'

data_load_state = st.text('Loading data...')

data = pd.read_csv(DATA_URL)

data_load_state.text('Loading data...done!')



st.write('Would you like to see the raw data?')

# Option to view raw data
if st.checkbox(''):
    st.subheader('Raw data')
    st.write(data)

st.write('## Looking at the individual columns')

st.write('Please choose a column header to explore')

cols = list(data.columns)
col_select = st.selectbox('Select:', cols)

st.write('Column:', col_select)
st.write('There are', data[col_select].isna().sum(), 'missing values.')
st.write('There are', data[col_select].nunique(), 'unique values.')
st.write('The value counts:')
st.write(data[col_select].value_counts())




st.write('## What relationships can we find?')

num = st.number_input('Enter a number', 10)

st.write('Looking at the top', num, 'most active users and the number of documents they have sent.')

# Create separate cols for date info
data_2 = data
data_2['Year'] = data_2['Date'].str[-4:]
data_2['Month'] = data_2['Date'].str[3:5]
data_2['mm/yyyy'] = data_2['Date'].str[-7:]

# Create pivot table for Users and number of unique sessions and total docs sent
pivot_user = pd.pivot_table(data_2, 
                            index=['User'], 
                            values=['Document', 'Session'], 
                            aggfunc=[pd.Series.nunique, 'count'])
# Drop non-unique session count
pivot_user.drop(('count', 'Session'), axis=1, inplace=True)
# Drop unique doc count
pivot_user.drop(('nunique', 'Document'), axis=1, inplace=True)
# Sort in decending order on session count
pivot_user_sorted = pivot_user.sort_values(('nunique','Session'), ascending=False)

# Create a graphs to visualise this relationship
fig, ax = plt.subplots()
plt.title(f'Top {num} users and number of docs sent')

ax = pivot_user_sorted[:num][('nunique', 'Session')].plot(kind='bar', label='Count(sessions)')

ax1 = pivot_user_sorted[:num][('count', 'Document')].plot(kind='line', secondary_y=True, color='red', label='Count(docs-sent)')

ax.set_xlabel('User')
ax.set_ylabel('Count(sessions)')
ax1.set_ylabel('Count(docs-sent)')

# Removing x-labels, the pseudonymised userIDs
ax.set_xticklabels([])

plt.legend()
st.pyplot(fig)

st.write('On average', np.mean(pivot_user_sorted[:num][('count', 'Document')]), 'documents are sent in the top', num, 'users.')




st.write('### How does usage vary over time?')
st.write('''
Please select; 
\n* Collections to view the number of unique collections viewed per month 
\n* Document to view the number of unique documents viewed per month 
\n* Recipient to view the number of unique recipients per month 
\n* Session to view the number of unique sessions per month 
\n* User to view the number of unique users per month.
''')

# Pivot table on year, looking at:
# number of unique Collections viewed
# number of unique Documents viewed
# number of unique email Recipients
# number of Sessions
# number of unique Users active in that month

pivot_date = pd.pivot_table(data_2, 
                            index=['Year', 'Month'], 
                            values=['Collection', 'Document', 'Recipient', 'Session', 'User'], 
                            aggfunc=pd.Series.nunique)

pivot_cols = list(pivot_date.columns)
pivot_col_select = st.selectbox('Please select a variable:', pivot_cols)
st.write(pivot_date[pivot_col_select])
fig = plt.figure()
ax = pivot_date[pivot_col_select].plot(kind='bar', rot=0)
ax.set_title(f'Number of unique {pivot_col_select.lower()}\'s per month')
ax.set_ylabel('Count')

st.pyplot(fig)


st.write('''
### Looking at the 'Event Type' column
\nNow we will see how the users have interacted with the app each month. Please select;
\n* ASSET_SHARE to view the number of documents that have been shared.
\n* ASSET_VIEW to view the number of documents that have been viewed.
\n* COLLECTION_VIEW to view the number of collections that have been accessed.
''')

# Pivot table on year, looking at number of event types showing what the app is mainly used for

pivot_event = pd.pivot_table(data_2, 
                             index=['Year', 'Month'], 
                             columns=['Event Type'], 
                             values=['User'], 
                             aggfunc='count', 
                             fill_value=0)

pivot_event_dropped = pivot_event.drop([('User', 'APP_CONTENT_INTERACTION'), 
                                        ('User', 'ASSET_SHARE_FAILED'), 
                                        ('User', 'LOGIN'), 
                                        ('User', 'PLUGIN'), 
                                        ('User', 'PLUGIN_CONTENT_INTERACTION'), 
                                        ('User', 'PLUGIN_OPENED')], axis=1)

piv_event_cols = pivot_event_dropped.columns
piv_event_select = st.selectbox('Please choose Event Type:', piv_event_cols)
st.write(pivot_event_dropped[piv_event_select])
fig = plt.figure()
ax = pivot_event_dropped[piv_event_select].plot(kind='bar', rot=0)
ax.set_title(f'Event {piv_event_select[1].lower()} usage over time')
ax.set_ylabel('Count')
st.pyplot(fig)
