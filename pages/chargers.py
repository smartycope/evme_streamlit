import streamlit as st
import requests
from streamlit import session_state as ss

st.title("Chargers")

# url = "https://api.openchargemap.io/v3"
# params = {
#     "key": st.secrets.OPEN_CHARGEMAP_API_KEY,
# }

# st.html('<iframe src="https://openchargemap.org/site" width="100%" height="600px"></iframe>')
st.markdown("""
<iframe src="https://openchargemap.org/site" width="100%" height="600px"></iframe>
""", unsafe_allow_html=True)