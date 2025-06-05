import streamlit as st
import requests
from streamlit import session_state as ss

def lookup_vin(vin):
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        decoded_info = {entry["Variable"]: entry["Value"] for entry in data["Results"] if entry["Value"]}
        return decoded_info, data
    else:
        return {"Error": "Failed to retrieve data"}

with st.expander("VIN Lookup"):
    st.title("Vehicle VIN Lookup")
    vin = st.text_input("Enter a VIN number:")

    if vin:
        with st.spinner("Looking up VIN..."):
            vin_data, raw = lookup_vin(vin)
            if "Error" in vin_data:
                st.error(vin_data["Error"])
            else:
                st.json(vin_data)


if "idx" not in ss:
    ss.idx = 0
if "info" not in ss:
    ss.info = {}

STEPS = 9

def back_next():
    l, r = st.columns(2)
    if r.form_submit_button("Next"):
        ss.idx = min(STEPS, ss.idx + 1)
        st.rerun()
    if l.form_submit_button("Back"):
        ss.idx = max(0, ss.idx - 1)
        st.rerun()

# Current Situation (Input)
st.progress(ss.idx/STEPS)
match ss.idx:
    case 0:
        with st.form("current_car"):
            st.title("Current Car")
            ss.info["year"] = st.text_input("Year", ss.info.get("year", ""))
            makes = ["Toyota", "Honda", "Ford", "Chevrolet", "Dodge", "BMW", "Audi", "Mercedes", "Jaguar", "Porsche"]
            ss.info["make"] = st.selectbox("Make", makes, makes.index(ss.info.get("make", makes[0])))
            models = ["Camry", "Civic", "Mustang", "Impala", "Charger", "M3", "A4", "C300", "XE", "911"]
            ss.info["model"] = st.selectbox("Model", models, models.index(ss.info.get("model", models[0])))
            trims = ["Base", "Premium", "Luxury"]
            ss.info["trim"] = st.selectbox("Trim", trims, trims.index(ss.info.get("trim", trims[0])))
            ss.info["vin"] = st.text_input("VIN", ss.info.get("vin", ""))
            back_next()
    case 1:
        with st.form("Stats"):
            st.title("Stats")
            ss.info["mileage"] = st.number_input("Mileage", min_value=0, value=ss.info.get("mileage", 0))
            ownership = ["Own", "Financed", "Leased"]
            ss.info["ownership"] = st.selectbox("Ownership", ownership, ownership.index(ss.info.get("ownership", "Own")))
            title_status = ["Clean", "Branded", "Rebuilt", "Salvage"]
            ss.info["title_status"] = st.selectbox("Title Status", title_status, title_status.index(ss.info.get("title_status", "Clean")))
            condition = ["Poor", "Fair", "Good", "Excellent"]
            ss.info["condition"] = st.selectbox("Condition", condition, condition.index(ss.info.get("condition", "Good")))
            ss.info["modifications"] = st.text_input("Modifications", ss.info.get("modifications", ""))
            ss.info["tires"] = st.text_input("Tires", ss.info.get("tires", ""))
            back_next()
    case 2:
        with st.form("Ownership"):
            st.title("Ownership")
            ownership = ["Own", "Financed", "Leased"]
            ss.info["ownership"] = st.selectbox("Ownership", ownership, ownership.index(ss.info.get("ownership", "Own")))
            back_next()
    case 3:
        with st.form("Financials"):
            st.title("Financials")
            if ss.info["ownership"] == "Financed":
                ss.info["monthly_payment"] = st.number_input("Monthly Payment", min_value=0, value=ss.info.get("monthly_payment", 0))
                ss.info["when_bought"] = st.date_input("When Bought", ss.info.get("when_bought", None))
                ss.info["how_long_on_loan"] = st.number_input("How Long on Loan", min_value=0, value=ss.info.get("how_long_on_loan", 0))
                ss.info["how_many_months_left_on_loan"] = st.number_input("How Many Months Left on Loan", min_value=0, value=ss.info.get("how_many_months_left_on_loan", 0))
                ss.info["interest_rate"] = st.number_input("Interest Rate", min_value=0.0, max_value=100.0, value=ss.info.get("interest_rate", 0.0))
            if ss.info["ownership"] == "Leased":
                ss.info["residuals"] = st.number_input("Residuals", min_value=0, value=ss.info.get("residuals", 0))
                ss.info["buyout"] = st.number_input("Buyout", min_value=0, value=ss.info.get("buyout", 0))
                ss.info["ending_term"] = st.number_input("Ending Term", min_value=0, value=ss.info.get("ending_term", 0))
                ss.info["monthly_payment"] = st.number_input("Monthly Payment", min_value=0, value=ss.info.get("monthly_payment", 0))
            back_next()
    case 4:
        with st.form("Insurance"):
            st.title("Insurance")
            insurance = ["Owned", "Leased", "Other"]
            ss.info["insurance"] = st.selectbox("Insurance", insurance, insurance.index(ss.info.get("insurance", "Owned")))
            back_next()
    case 5:
        with st.form("Driving"):
            st.title("Driving")
            driving = ["Owner", "Renter", "Leased", "Other"]
            ss.info["driving"] = st.selectbox("Driving status", driving, driving.index(ss.info.get("driving", "Owner")))
            back_next()
    case 6:
        with st.form("Location"):
            st.title("Location")
            location = ["Home", "Work", "Other"]
            ss.info["location"] = st.selectbox("Location", location, location.index(ss.info.get("location", "Home")))
            back_next()
    case 7:
        with st.form("Preferences"):
            st.title("Preferences")
            preferences = ["Electric", "Hybrid", "Other"]
            ss.info["preferences"] = st.selectbox("Preferences", preferences, preferences.index(ss.info.get("preferences", "Electric")))
            back_next()
    case 8:
        with st.form("Finances"):
            st.title("Finances")
            ss.info["finances"] = st.number_input("Finances", min_value=0, value=ss.info.get("finances", 0))
            back_next()
    case 9:
        if st.button("Take again"):
            ss.idx = 0
            st.balloons()
            ss.info = {}
            st.success("Success!")
            st.rerun()
        ss.info


