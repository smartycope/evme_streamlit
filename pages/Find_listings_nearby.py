import streamlit as st
import requests
from streamlit import session_state as ss

st.title("Find listings nearby")
@st.cache_data
def get_listings(**kwargs):
    """Get listings from auto.dev"""
    url = "https://auto.dev/api/listings"
    params = {k: v for k, v in kwargs.items() if v is not None}
    params.update({
        "apikey": st.secrets.AUTO_DEV_API_KEY,
    })
    response = requests.get(url, params=params)
    return response.json()

search_by_make_model = st.checkbox("Search for a specific make/model")
def query(func, *args, checked=True, **kwargs):
    l, r = st.columns(2)
    with l:
        val = func(*args, **kwargs)
    include = r.checkbox(f"Include?", key=args[0], value=checked)
    return val if include else None


with st.form("Find listings"):
    st.title("Find listings")

    fuel_type = query(st.multiselect, "Fuel Type", [
        "gasoline",
        "hybrid",
        "electric",
        "flex fuel",
        "natural gas",
        "plug-in hybrid",
        "hydrogen fuel cell",
        "diesel",
    ], default='electric')
    price_max = query(st.number_input, "Price Max", min_value=0, value=60000)
    city = query(st.text_input, "City", value="Boise")
    state = query(st.text_input, "State", value="ID")
    radius = query(st.number_input, "Radius (miles)", min_value=0, value=50)
    exclude_no_price = query(st.checkbox, "Exclude No Price", value=True)
    year_min = query(st.number_input, "Year Min", min_value=1900, max_value=3000, value=2016, checked=False)
    exterior_color = query(st.multiselect, "Exterior Color", ['black', 'white', 'gray', 'brown', 'red', 'blue', 'silver', 'green', 'orange', 'purple', 'gold'], checked=False)
    interior_color = query(st.multiselect, "Interior Color", ['black', 'white', 'gray', 'brown', 'red', 'blue'], checked=False)
    driveline = query(st.multiselect, "Driveline", ['RWD', 'FWD', '4X4', 'AWD'], checked=False)
    exclude_regional = query(st.checkbox, "Exclude Regional", value=True, checked=False)
    body_style = query(st.multiselect, "Body Style", ['convertible', 'coupe', 'minivan', 'sedan', 'wagon', 'suv', 'truck', 'crossover', 'passenger_cargo_vans'], checked=False)
    features = query(st.multiselect, "Features", [
        'backup_camera',
        'bluetooth',
        'entertainment',
        'handicap_accessible',
        'heated_seats',
        'ipod_aux_input',
        'lane_departure_warning_system',
        'leather',
        'navigation',
        'one_owner',
        'roof_rack',
        'sunroof',
        'third_row_seats',
        'towing',
        'warranty',
    ], checked=False)
    category = query(st.multiselect, "Category", ["american", "classic", "commuter", "electric", "family", "fuel_efficient", "hybrid", "large", "muscle", "off_road", "small", "sport", "supercar"], checked=False)
    condition = query(st.multiselect, "Condition", ["new", "used", "certified pre-owned"], checked=False)
    cabin = query(st.multiselect, 'Cabin', ['crew', 'extended', 'regular'], checked=False)
    bed = query(st.multiselect, 'Bed', ['regular', 'short', 'long', 'step-side', 'chassis'], checked=False)
    rear_wheel = query(st.multiselect, 'Rear Wheel', ['dual', 'single'], checked=False)

    sort_filter = st.selectbox("Sort by", ["Price", "Mileage", "Year", "Distance", "Created_At"], index=0)
    sort_order = st.selectbox("Sort order", ["Asc", "Desc"], index=0)

    if search_by_make_model:
        make, model, year = ss.get_make_model_year()
    else:
        make = model = year = None

    if st.form_submit_button("Find listings"):
        q = {
            "radius": radius,
            "price_max": price_max,
            "year_min": year_min,
            "city": city,
            "state": state,
            "exterior_color": exterior_color,
            "interior_color": interior_color,
            "driveline": driveline,
            "exclude_regional": exclude_regional,
            "exclude_no_price": exclude_no_price,
            "body_style": body_style,
            "features": features,
            "category": category,
            "condition": condition,
            "fuel_type": fuel_type,
            "cabin": cabin,
            "bed": bed,
            "rear_wheel": rear_wheel,
            "sort_filter": sort_filter.lower() + ':' + sort_order.lower(),
        }
        if make is not None and model is not None and year is not None:
            q.update({
                "make": make,
                "model": model,
                "year": year,
            })
        listings = get_listings(**{k: v for k, v in q.items() if v is not None})
        # st.json(listings)

        # Display the listings nicely
        for listing in listings['records']:
            vin = listing['vin']
            year = listing['year']
            make = listing['make']
            model = listing['model']
            price = listing['price']
            mileage = listing['mileage']
            city = listing['city']
            state = listing['state']
            lat = listing['lat']
            lon = listing['lon']
            primary_photo_url = listing['primaryPhotoUrl']
            condition = listing['condition']
            dealer_name = listing['dealerName']
            active = listing['active']
            created_at = listing['createdAt']
            dealerName = listing['dealerName']
            trim = listing['trim']
            bodyStyle = listing['bodyStyle']
            bodyType = listing['bodyType']
            mileageHumanized = listing['mileageHumanized']
            recentPriceDrop = listing['recentPriceDrop']
            eligibleForFinancing = listing['eligibleForFinancing']
            photoUrls = listing['photoUrls']
            isHot = listing['isHot']
            distanceFromOrigin = listing['distanceFromOrigin']
            monthlyPayment = listing['monthlyPayment']
            clickoffUrl = listing['clickoffUrl']

            with st.expander(f"{year} {make} {model}, {mileageHumanized} @ {dealer_name} for {price}"):
                try:
                    st.image(primary_photo_url)
                except Exception as e:
                    st.error(f'Failed to load image: {e}')
                st.write(f"""
                    Price: {price}
                    Trim: {trim}
                    Body Style: {bodyStyle}
                    Body Type: {bodyType}
                    Condition: {condition}
                    Mileage: {mileage} miles
                    Distance: {distanceFromOrigin} miles
                    Monthly Payment: {monthlyPayment}
                    Dealer: {dealer_name}
                    Vin: {vin}
                    Created At: {created_at}
                    Active: {active}
                    Is Hot: {isHot}
                    Eligible for Financing: {eligibleForFinancing}
                    Recent Price Drop: {recentPriceDrop}
                """.replace('\n', '\n\n'))
                # st.write(f"Photo URLs: {photoUrls}")
                if clickoffUrl:
                    st.markdown(f"[Link]({clickoffUrl})")








