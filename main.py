import streamlit as st
import requests

def lookup_vin(vin):
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        decoded_info = {entry["Variable"]: entry["Value"] for entry in data["Results"] if entry["Value"]}
        return decoded_info, data
    else:
        return {"Error": "Failed to retrieve data"}

st.title("Vehicle VIN Lookup")
vin = st.text_input("Enter a VIN number:")

if vin:
    with st.spinner("Looking up VIN..."):
        vin_data, raw = lookup_vin(vin)
        if "Error" in vin_data:
            st.error(vin_data["Error"])
        else:
            st.json(vin_data)
        st.json(raw)
