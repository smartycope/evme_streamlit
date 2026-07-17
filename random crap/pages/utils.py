import streamlit as st
import requests
from streamlit import session_state as ss

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

def get_trims(year, make, model):
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeYear/make/{make}/modelyear/{year}/model/{model}?format=json"
    res = requests.get(url).json()
    return sorted({item['Trim'] for item in res['Results']})

def get_mmyt(current_year=None, current_make=None, current_model=None, current_trim=None):
    years = list(range(1980, 2025))[::-1]
    year = st.selectbox(
        "Year",
        years,
        placeholder='Select a year',
        index=years.index(current_year) if current_year is not None else None
    )
    makes = get_all_car_makes()
    make = st.selectbox(
        "Make",
        makes,
        index=makes.index(current_make) if current_make is not None else None,
        placeholder='Select a make'
    )
    can_get_models = make is not None and year is not None
    models = get_models(year, make) if can_get_models else []
    model = st.selectbox(
        "Model",
        models,
        index=models.index(current_model) if current_model is not None else None,
        placeholder='Select a model', disabled=not can_get_models
    )
    trims = get_trims(year, make, model) if can_get_models else []
    trim = st.selectbox(
        "Trim",
        trims,
        index=trims.index(current_trim) if current_trim is not None else None,
        placeholder='Select a trim', disabled=not can_get_models
    )
    return make, model, year, trim

"""
def get_make_model_year(current_year=None, current_make=None, current_model=None):
    years = list(range(1980, 2025))[::-1]
    year = st.selectbox(
        "Year",
        years,
        placeholder='Select a year',
        index=years.index(current_year) if current_year is not None else None
    )
    makes = get_all_car_makes()
    make = st.selectbox(
        "Make",
        makes,
        index=makes.index(current_make) if current_make is not None else None,
        placeholder='Select a make'
    )
    can_get_models = make is not None and year is not None
    models = get_models(year, make) if can_get_models else []
    model = st.selectbox(
        "Model",
        models,
        index=models.index(current_model) if current_model is not None else None,
        placeholder='Select a model', disabled=not can_get_models
    )
    return make, model, year
 """