"""A small Streamlit prototype for searching dealership EV listings."""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt
from typing import Any

import requests
import streamlit as st

API_URL = "https://api.auto.dev/listings"
ZIP_API_URL = "https://auto.dev/api/zip"
RESULTS_PER_PAGE = 10
SEARCH_PARAMS_KEY = "listing_search_params"
TOTAL_RESULTS_KEY = "listing_total_results"
PAGE_KEY = "listing_page"


@st.cache_data(ttl=300, show_spinner=False)
def get_listings(params: dict[str, Any]) -> dict[str, Any]:
    """Fetch a page of active dealership listings from Auto.dev."""
    response = requests.get(
        API_URL,
        params=params,
        headers={"Authorization": f"Bearer {st.secrets['AUTO_DEV_API_KEY']}"},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=86_400, show_spinner=False)
def get_zip_coordinates(zip_code: str) -> tuple[float, float]:
    """Return the longitude and latitude for a ZIP code from Auto.dev."""
    response = requests.get(
        f"{ZIP_API_URL}/{zip_code}",
        headers={"Authorization": f"Bearer {st.secrets['AUTO_DEV_API_KEY']}"},
        timeout=20,
    )
    response.raise_for_status()
    location = response.json()["payload"]
    return float(location["longitude"]), float(location["latitude"])


def distance_in_miles(
    origin: tuple[float, float] | None, location: Any
) -> str:
    """Calculate the straight-line distance between the search ZIP and listing."""
    if origin is None or not isinstance(location, list) or len(location) != 2:
        return "—"

    try:
        origin_lon, origin_lat = origin
        listing_lon, listing_lat = map(float, location)
        lat_difference = radians(listing_lat - origin_lat)
        lon_difference = radians(listing_lon - origin_lon)
        haversine = (
            sin(lat_difference / 2) ** 2
            + cos(radians(origin_lat))
            * cos(radians(listing_lat))
            * sin(lon_difference / 2) ** 2
        )
        return f"{2 * 3_958.8 * asin(sqrt(haversine)):,.0f} mi"
    except (TypeError, ValueError):
        return "—"


def listing_rows(
    listings: list[dict[str, Any]], origin: tuple[float, float] | None = None
) -> list[dict[str, str]]:
    """Shape the API response into the concise table used by the prototype."""
    rows = []
    for listing in listings:
        vehicle = listing.get("vehicle") or {}
        retail = listing.get("retailListing") or {}
        if not retail:
            continue

        year = vehicle.get("year", listing.get("year"))
        make = vehicle.get("make", listing.get("make"))
        model = vehicle.get("model", listing.get("model"))
        vehicle_name = " ".join(str(part) for part in (year, make, model) if part)
        price = retail.get("price", listing.get("price"))
        distance = listing.get("distance", listing.get("distanceFromOrigin"))
        listing_url = retail.get("vdp") or listing.get("clickoffUrl") or listing.get("vdpUrl")

        rows.append(
            {
                "Dealership": str(retail.get("dealer") or listing.get("dealerName") or "—"),
                "Vehicle": vehicle_name or "—",
                "Distance": (
                    f"{float(distance):,.0f} mi"
                    if distance is not None
                    else distance_in_miles(origin, listing.get("location"))
                ),
                "Price": f"${float(price):,.0f}" if price is not None else "—",
                "Location": ", ".join(
                    str(part)
                    for part in (
                        retail.get("city") or listing.get("city"),
                        retail.get("state") or listing.get("state"),
                    )
                    if part
                )
                or "—",
                "Listing": listing_url or "",
            }
        )
    return rows


st.set_page_config(page_title="EV Listings", page_icon="⚡", layout="wide")
st.title("Find EV listings")
st.caption("Search active dealership listings. Leave every field blank to browse electric vehicles nationwide.")

with st.form("ev-listing-search"):
    first_column, second_column = st.columns(2)
    with first_column:
        year = st.text_input("Year", placeholder="e.g. 2023")
        make = st.text_input("Make", placeholder="e.g. Tesla")
        model = st.text_input("Model", placeholder="e.g. Model 3")
    with second_column:
        zip_code = st.text_input("ZIP code", max_chars=5, placeholder="e.g. 83702")
        radius = st.number_input("Radius (miles)", min_value=1, max_value=500, value=50, step=5)

    submitted = st.form_submit_button("Find EV listings", type="primary")

if submitted:
    clean_zip = zip_code.strip()
    if clean_zip and (not clean_zip.isdigit() or len(clean_zip) != 5):
        st.error("Enter a valid 5-digit ZIP code.")
        st.session_state.pop(SEARCH_PARAMS_KEY, None)
        st.session_state.pop(TOTAL_RESULTS_KEY, None)
    else:
        params: dict[str, Any] = {
            "vehicle.fuel": "Electric",
            "limit": RESULTS_PER_PAGE,
            "includes": "total",
            "sort": "updatedAt.desc",
        }
        if year.strip():
            params["vehicle.year"] = year.strip()
        if make.strip():
            params["vehicle.make"] = make.strip()
        if model.strip():
            params["vehicle.model"] = model.strip()
        if clean_zip:
            params["zip"] = clean_zip
            params["distance"] = radius

        st.session_state[SEARCH_PARAMS_KEY] = params
        st.session_state.pop(TOTAL_RESULTS_KEY, None)
        st.session_state[PAGE_KEY] = 1

search_params = st.session_state.get(SEARCH_PARAMS_KEY)
if search_params:
    saved_total = st.session_state.get(TOTAL_RESULTS_KEY)
    pagination_slot = st.empty()
    current_page = 1

    if isinstance(saved_total, int):
        total_pages = max(1, (saved_total + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE)
        current_page = pagination_slot.pagination(
            total_pages,
            key=PAGE_KEY,
            width="content",
        )

    try:
        with st.spinner("Searching active EV listings..."):
            payload = get_listings({**search_params, "page": current_page})
    except requests.RequestException as error:
        st.error("Auto.dev could not complete the search. Please try again shortly.")
        st.caption(f"API error: {error}")
    else:
        listings = payload.get("data", payload.get("records", []))
        origin = None
        if search_params.get("zip"):
            try:
                origin = get_zip_coordinates(search_params["zip"])
            except (KeyError, TypeError, ValueError, requests.RequestException):
                st.warning("Listings were found, but their distances could not be calculated.")

        rows = listing_rows(listings, origin)
        total = payload.get("total")
        if isinstance(total, int):
            st.session_state[TOTAL_RESULTS_KEY] = total
            if not isinstance(saved_total, int):
                total_pages = max(1, (total + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE)
                pagination_slot.pagination(total_pages, key=PAGE_KEY, width="content")

        if not rows:
            st.info("No active EV listings matched this search.")
        else:
            total_message = f" of {total:,}" if isinstance(total, int) else ""
            st.subheader(
                f"Page {current_page} · Showing {len(rows):,}{total_message} active EV listings"
            )
            st.dataframe(
                rows,
                column_config={
                    "Listing": st.column_config.LinkColumn("Listing", display_text="View listing"),
                },
                hide_index=True,
                width='content',
            )
