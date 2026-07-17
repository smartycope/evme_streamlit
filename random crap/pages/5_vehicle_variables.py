import streamlit as st
import requests
import pandas as pd
from streamlit import session_state as ss

@st.cache_data
def vehicle_variables():
    url = "https://vpic.nhtsa.dot.gov/api/vehicles/getvehiclevariablelist?format=json"
    res = requests.get(url).json()
    return res['Results']

st.title("Vehicle Variables Reference")
"These are all the available fields we have to work with"

# Also show it as a table
df = pd.DataFrame(vehicle_variables())
df = df[['Name', 'Description', 'DataType', 'GroupName']]
st.dataframe(df)

for i in vehicle_variables():
    with st.expander(i['Name']):
        st.html(i['Description'])

