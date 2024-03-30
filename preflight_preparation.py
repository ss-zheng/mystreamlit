"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
from datetime import datetime
import pandas as pd
import requests
import pytz


def utc2pst(utc_string):
    # The given date and time in YYYY-MM-DD HH:MM:SS format
    given_date_str = utc_string
    # Convert the given date string to a datetime object
    given_date = datetime.strptime(given_date_str, "%Y-%m-%d %H:%M:%S")
    # Assuming the given datetime is in UTC, we'll set the timezone to UTC
    given_date_utc = given_date.replace(tzinfo=pytz.utc)
    # Convert the UTC datetime to PST
    pst_time = given_date_utc.astimezone(pytz.timezone('US/Pacific'))
    # The result is a datetime object with PST timezone information
    return pst_time.strftime("%Y-%m-%d %H:%M:%S")

# def metar_and_taf(airport_ids):
#     headers = {
#         'accept': '*/*',
#     }

#     params = {
#         'ids': airport_ids if type(airport_ids) == str else ",".join(airport_ids),
#         'format': 'json',
#         'taf': 'true',
#     }

#     response = requests.get('https://aviationweather.gov/api/data/metar', params=params, headers=headers)
    
#     return response.json()


def aviationweather_general(icao_id, info):
    headers = {
        'accept': '*/*',
    }

    params = {
        'ids': icao_id,
        'format': 'json',
    }
    if info == "pirep":
        params = {
            'id': icao_id,
            'format': 'json',
        }

    response = requests.get(f'https://aviationweather.gov/api/data/{info}', params=params, headers=headers)
    return response.json()

def atis(icao_id):
    url = f"https://atisgenerator.com/api/v1/airports/{icao_id}/atis"
    payload = {
        "ident": "A",
        "icao": "KJAX",
        "remarks1": "Custom remarks.",
        "remarks2": {},
        "landing_runways": ["08", "26"],
        "departing_runways": ["08", "26"],
        "output-type": "atis",
        "override_runways": False,
        "metar": "KJAX 201853Z 00000KT 10SM FEW250 28/22 A3000 RMK AO2 SLP159 T02780217"
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def runways(icao_id):
    url = f"https://atisgenerator.com/api/v1/airports/{icao_id}/runways"
    response = requests.get(url)
    return response.json()

# def metar_and_taf_callback():
#     airport_ids = st.session_state['metar_and_taf']
#     metar_and_taf_info = metar_and_taf(airport_ids)
#     st.write(metar_and_taf_info)

st.title(":airplane_departure: :blue[PPL] Preflight Preparation")
st.markdown(
        "Author: [Dan. Z](https://www.danzss.com) | [X/Twitter](https://twitter.com/zssdan)"
        )
# st.divider()

st.header(":mostly_sunny: METAR and TAF", divider="rainbow")
airport_ids = st.multiselect(
    'Select Airport IDs',
    ['CYXX', 'CYVR', 'CYPK', 'CYHE'],
    ['CYXX'],
    key="metar_and_taf"
    )
    # this api only have CYXX and CYVR, also CYHE(no taf) ['CYXX', 'CYPK', 'CYHE', 'CZBB', 'CYVR'],
    
for icaoId in airport_ids:
    
    airport_info = aviationweather_general(icaoId, "airport")[0]
    # station_info = aviationweather_general(icaoId, "stationinfo")
    metar_info = aviationweather_general(icaoId, "metar")
    taf_info = aviationweather_general(icaoId, "taf")
    pirep_info = aviationweather_general(icaoId, "pirep")
    
    # st.write(station_info)
    # st.write(airport_info)
    st.write(f"**{airport_info['id']} - {airport_info['name']}, {airport_info['state']} {airport_info['country']}**")
    for freq in airport_info["freqs"]:
        st.write(f"{freq['type']}: {freq['freq']}")
    
    tabs = []
    tabs_info = []
    if metar_info:
        tabs.append("metar")
        tabs_info.append(metar_info)
    if taf_info:
        tabs.append("taf")
        tabs_info.append(taf_info)
    if pirep_info:
        tabs.append("pirep")
        tabs_info.append(pirep_info)

    if not tabs:
        continue

    st_tabs = st.tabs(tabs)

    for st_tab, tab_info in zip(st_tabs, tabs_info):
        with st_tab:
            content = tab_info[0]["rawOb"] if "rawOb" in tab_info[0] else tab_info[0]["rawTAF"]
            format_content = content.replace("BECMG", "\nBECMG")
            format_content = format_content.replace("FM", "\nFM")
            format_content = format_content.replace("PROB", "\nPROB")
            format_content = format_content.replace("RMK", "\nRMK")
            # st.write(tab_info)
            st.code(format_content, language="bash")


    # airport_info = metar_and_taf(icaoId)[0]
    # # st.write(airport_info)
    # pst_time_str = utc2pst(airport_info["reportTime"])
    # # # **{airport_info["icaoId"]} - {airport_info["name"]}**
    # # `{atis_info["data"]["text"]}`

    # st.markdown(f"""
    # #### {airport_info["icaoId"]} - {airport_info["name"]}

    # Report Time: {pst_time_str} PST

    # `{airport_info["rawOb"]}`

    # `{airport_info["rawTaf"]}`
    # """)

st.header(":scales: C-172S WEIGHT AND BALANCE SHEET", divider="rainbow")
aircraft = st.selectbox("Aircraft", ["C-FAQA", "C-FMNB", "C-CAU"])
passenger_weight = st.slider(
        "Pilot & Front Passengers",
        min_value=100,
        max_value=500,
        value=360,
        step=5
        )
fuel_weight = st.slider(
        "Fuel(6lbs/US Gal)",
        min_value=10,
        max_value=56,
        value=20,
        step=1
        )
duration = st.number_input("Flight Hours",
                min_value=0.5,
                max_value=2.0,
                value=1.0,
                step=0.5
                )
fuel_burn_weight = duration * 60

others = st.checkbox("others")

rear_seats_weight = 0
baggage_area1_weight = 0
baggage_area2_weight = 0
if others:
    rear_seats_weight = st.number_input("Rear Seats",
                    min_value=0,

                    max_value=200,
                    value=0,
                    step=1
                    )
    baggage_area1_weight = st.number_input("Baggage Area 1",
                    min_value=0,
                    max_value=200,
                    value=0,
                    step=1
                    )
    baggage_area2_weight = st.number_input("Baggage Area 2",
                    min_value=0,
                    max_value=200,
                    value=0,
                    step=1
                    )
    

weight_and_balance_dict = {
        "C-FAQA": {"item": "Basic Empty Weight", "weight": 1665.47, "arm": 39.06, "moment": 65055.33},
        "C-FMNB": {"item": "Basic Empty Weight", "weight": 1701, "arm": 40.08, "moment": 69876},
        "C-FCAU": {"item": "Basic Empty Weight", "weight": 1734, "arm": 43.85, "moment": 76044}
}

basic_empty_weight = weight_and_balance_dict[aircraft]
pilot_and_front_passengers = {"item": "Pilot & Front Passengers", "weight": passenger_weight, "arm": 37, "moment": passenger_weight * 37}
rear_seats = {"item": "Rear Seats", "weight": rear_seats_weight, "arm": 73, "moment": rear_seats_weight * 73}
baggage_area_1 = {"item": "Baggage Area 1", "weight": baggage_area1_weight, "arm": 95, "moment": baggage_area1_weight * 95}
baggage_area_2 = {"item": "Baggage Area 2", "weight": baggage_area2_weight, "arm": 123, "moment": baggage_area2_weight * 123}
zero_fuel_weight = {
        "item": "Zero Fuel Weight",
        "weight": basic_empty_weight["weight"] + pilot_and_front_passengers["weight"] + baggage_area_1["weight"] + baggage_area_2["weight"],
        "arm": -1,
        "moment": basic_empty_weight["moment"] + pilot_and_front_passengers["moment"] + baggage_area_1["moment"] + baggage_area_2["moment"],
        }
zero_fuel_weight["arm"] = zero_fuel_weight["moment"] / zero_fuel_weight["weight"]
fuel = {"item": "Fuel(6lbs/US Gal)", "weight": fuel_weight * 6, "arm": 48, "moment": fuel_weight * 6 * 48}
take_off_weight = {
        "item": "Take-Off Weight",
        "weight": fuel["weight"] + zero_fuel_weight["weight"], 
        "arm": -1, 
        "moment": fuel["moment"] + zero_fuel_weight["moment"]
        }
take_off_weight["arm"] = take_off_weight["moment"] / take_off_weight["weight"]
fuel_burn = {"item": "Fuel Burn", "weight": -fuel_burn_weight, "arm": 48, "moment": -fuel_burn_weight * 48}
landing_weight = {
        "item": "Landing Weight",
        "weight": take_off_weight["weight"] + fuel_burn["weight"],
        "arm": -1,
        "moment": take_off_weight["moment"] + fuel_burn["moment"]
        }
landing_weight["arm"] = landing_weight["moment"] / landing_weight["weight"]



df = pd.DataFrame([
    basic_empty_weight,
    pilot_and_front_passengers,
    rear_seats,
    baggage_area_1,
    baggage_area_2,
    zero_fuel_weight,
    fuel,
    take_off_weight,
    fuel_burn,
    landing_weight
    ])

        # df.style.hide(axis="index"),
        # df.style.apply(color_coding, axis=1),
        # df.style.highlight_max(axis=0),

def color_coding(row):
    if row["item"] in ["Zero Fuel Weight", "Take-Off Weight", "Landing Weight"]:
        return ['background-color:green'] * len(row)
    return ['background-color:transparent'] * len(row)

# st.table(df)

st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "weight": st.column_config.NumberColumn(
                "WEIGHT(LBS)",
                help="Weight in LBS",
                # min_value=0,
                # max_value=200,
                step=1,
                # format="%d lb(s)",
                # width="medium",
                required=True,
            ),
            "arm": st.column_config.NumberColumn(
                "ARM(in)",
                help="Arm in in",
                min_value=0,
                max_value=200,
                step=1,
                # format="%.2f",
                # width="medium",
                required=True,
            ),
            "moment": st.column_config.NumberColumn(
                "MOMENT",
                help="MOMENT",
                # min_value=0,
                # max_value=200,
                step=1,
                # format="%.2f",
                # width="medium",
                required=True,
            )
            }
        )

st.header("Appendix", divider="rainbow")
with st.expander("CYXX AERODROM CHART"):
    st.image("CYXX.jpg")
