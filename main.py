import streamlit as st
import requests
from streamlit import session_state as ss


if "idx" not in ss:
    ss.idx = 0
if "info" not in ss:
    ss.info = {}

STEPS = 9

def back_next(next=1, prev=1):
    l, r = st.columns(2)
    if r.form_submit_button("Next"):
        ss.idx = min(STEPS, ss.idx + next)
        st.rerun()
    if l.form_submit_button("Back"):
        ss.idx = max(0, ss.idx - prev)
        st.rerun()

@st.cache_data
def get_all_makes():
    url = "https://vpic.nhtsa.dot.gov/api/vehicles/getallmakes?format=json"
    res = requests.get(url).json()
    return sorted({item['MakeName'] for item in res['Results']})

@st.cache_data
def get_all_car_makes():
    url = "https://vpic.nhtsa.dot.gov/api/vehicles/GetMakesForVehicleType/car?format=json"
    res = requests.get(url).json()
    return sorted({item['MakeName'] for item in res['Results']})

@st.cache_data
def get_models(year, make):
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeYear/make/{make}/modelyear/{year}?format=json"
    res = requests.get(url).json()
    return sorted({item['Model_Name'] for item in res['Results']})


# Main form
if st.button('Clear info'):
    ss.info = {}
    st.rerun()

ss.info
st.progress(max(0, ss.idx)/STEPS)

match ss.idx:
    # Welcome screen
    case 0:
        """# Welcome to Vehicle Information Manager

        Click the button below to get started."""
        if st.button("Start"):
            ss.idx += 1
            st.rerun()

    # Current Car
    case 1:
        years = list(range(1980, 2025))[::-1]
        ss.info["year"] = st.selectbox(
            "Year",
            years,
            placeholder='Select a year',
            index=years.index(ss.info['year']) if 'year' in ss.info and ss.info['year'] is not None else None
        )
        makes = get_all_car_makes()
        ss.info["make"] = st.selectbox(
            "Make",
            makes,
            index=makes.index(ss.info['make']) if 'make' in ss.info and ss.info['make'] is not None else None,
            placeholder='Select a make'
        )
        can_get_models = 'make' in ss.info and ss.info['make'] is not None and 'year' in ss.info and ss.info['year'] is not None
        models = get_models(ss.info['year'], ss.info['make']) if can_get_models else []
        ss.info["model"] = st.selectbox(
            "Model",
            models,
            index=models.index(ss.info['model']) if 'model' in ss.info and ss.info['model'] is not None else None,
            placeholder='Select a model', disabled=not can_get_models
        )


        # Display the selection
        if st.button("Next"):
            ss.idx += 1
            st.rerun()

        # st.title("Current Car")
        # makes = ["Toyota", "Honda", "Ford", "Chevrolet", "Dodge", "BMW", "Audi", "Mercedes", "Jaguar", "Porsche"]
        # ss.info["make"] = st.selectbox("Make", makes, makes.index(ss.info.get("make", makes[0])), disabled=ss.info.get("year", None))
        # models = ["Camry", "Civic", "Mustang", "Impala", "Charger", "M3", "A4", "C300", "XE", "911"]
        # ss.info["model"] = st.selectbox("Model", models, models.index(ss.info.get("model", models[0])), disabled=ss.info.get("make", None))
        # trims = ["Base", "Premium", "Luxury"]
        # ss.info["trim"] = st.selectbox("Trim", trims, trims.index(ss.info.get("trim", trims[0])), disabled=ss.info.get("model", None))
        # ss.info["vin"] = st.text_input("VIN", ss.info.get("vin", ""))
        # back_next()
    # Stats of current car
    case 2:
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
    # Ownership
    case 3:
        with st.form("Ownership"):
            st.title("Ownership")
            ownership = ["Own", "Financed", "Leased"]
            ss.info["ownership"] = st.selectbox("Ownership", ownership, ownership.index(ss.info.get("ownership", "Own")))
            back_next(next=2 if ss.info["ownership"] == "Own" else 1)
    # Financials
    case 4:
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
    # Insurance
    case 5:
        with st.form("Insurance"):
            st.title("Insurance")
            insurance = ["Owned", "Leased", "Other"]
            ss.info["insurance"] = st.selectbox("Insurance", insurance, insurance.index(ss.info.get("insurance", "Owned")))
            back_next()
    # Driving
    case 6:
        with st.form("Driving"):
            st.title("Driving")
            driving = ["Owner", "Renter", "Leased", "Other"]
            ss.info["driving"] = st.selectbox("Driving status", driving, driving.index(ss.info.get("driving", "Owner")))
            back_next()
    # Location
    case 7:
        with st.form("Location"):
            st.title("Location")
            location = ["Home", "Work", "Other"]
            ss.info["location"] = st.selectbox("Location", location, location.index(ss.info.get("location", "Home")))
            back_next()
    # Preferences
    case 8:
        with st.form("Preferences"):
            st.title("Preferences")
            preferences = ["Electric", "Hybrid", "Other"]
            ss.info["preferences"] = st.selectbox("Preferences", preferences, preferences.index(ss.info.get("preferences", "Electric")))
            back_next()
    # Finances
    case 9:
        with st.form("Finances"):
            st.title("Finances")
            ss.info["finances"] = st.number_input("Finances", min_value=0, value=ss.info.get("finances", 0))
            back_next()
    # Submit
    case 10:
        st.success("Form submitted successfully!")
        st.balloons()
        st.json(ss.info)

        if st.button("Start Over"):
            ss.idx = 0
            ss.info = {}
            st.rerun()


