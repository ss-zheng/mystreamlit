"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import streamlit.components.v1 as components
from navcanada import navcanada_request
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import json
import requests
import pytz


def utc2pst(utc_string):
    formats = [
        "%Y-%m-%dT%H:%M:%S",  # ISO 8601 Format
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S%z",  # Extended Format with Timezone Information
        "%m/%d/%Y %I:%M:%S %p",  # US Format with AM/PM
        "%d-%m-%Y %H:%M",  # European Format with 24-hour Clock
        "%Y%m%d%H%M%S",  # Compact Format
        "%A, %B %d, %Y at %I:%M %p"  # Verbose Format
    ]
    given_date = None
    for fmt in formats:
        try:
            # Attempt to parse the datetime string with the current format
            given_date = datetime.strptime(utc_string, fmt)
        except ValueError:
            # If parsing fails, continue to the next format
            continue
    if not given_date:
        raise ValueError(f"Failed to parse {utc_string}")

    # Assuming the given datetime is in UTC, we'll set the timezone to UTC
    given_date_utc = given_date.replace(tzinfo=pytz.utc)
    # Convert the UTC datetime to PST
    pst_time = given_date_utc.astimezone(pytz.timezone('US/Pacific'))
    # The result is a datetime object with PST timezone information
    return pst_time.strftime("%Y-%m-%d %H:%M:%S %Z")

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

st.title(":airplane_departure: :blue[PPL] Preflight Preparation")
st.markdown(
        "Author: [Dan. Z](https://www.danzss.com) | [X/Twitter](https://twitter.com/zssdan)"
        )
# st.divider()

st.header(":mostly_sunny: Weather and NOTAM", divider="rainbow")
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
    notam_info = navcanada_request([icaoId], options={"alpha": ['notam']})
    
    # st.write(station_info)
    # st.write(airport_info)
    st.write(f"**{airport_info['id']} - {airport_info['name']}, {airport_info['state']} {airport_info['country']}**")
    
    if isinstance(airport_info["freqs"], list):
        for freq in airport_info["freqs"]:
            st.write(f"{freq['type']}: {freq['freq']}")
    elif isinstance(airport_info["freqs"], str):
            st.write(airport_info["freqs"])
    else:
        pass
    
    tabs = []
    tabs_info = []
    if metar_info:
        tabs.append("metar")
        tabs_info.append(metar_info)
    if taf_info:
        tabs.append("taf")
        tabs_info.append(taf_info)
    if notam_info:
        tabs.append("notam")
        tabs_info.append(notam_info)
    if pirep_info:
        tabs.append("pirep")
        tabs_info.append(pirep_info)

    if not tabs:
        continue

    st_tabs = st.tabs(tabs)

    for tab, st_tab, tab_info in zip(tabs, st_tabs, tabs_info):
        if tab == "notam":
            with st_tab:
                for notam in tab_info:
                    st.write(utc2pst(notam['startValidity']))
                    st.code(json.loads(notam["text"])["raw"], language="bash")
        else:
            with st_tab:
                content = tab_info[0]["rawOb"] if "rawOb" in tab_info[0] else tab_info[0]["rawTAF"]
                format_content = content.replace("BECMG", "\nBECMG")
                format_content = format_content.replace("FM", "\nFM")
                format_content = format_content.replace("PROB", "\nPROB")
                format_content = format_content.replace("RMK", "\nRMK")
                
                if any(key in tab_info[0] for key in ["reportTime", "issueTime"]):
                    utc_time_str = tab_info[0]['reportTime'] if 'reportTime' in tab_info[0] else tab_info[0]["issueTime"]
                    st.write(utc2pst(utc_time_str))
                st.code(format_content, language="bash")


st.header(":memo: Checklists", divider="rainbow")
with st.expander("Walk Around Checklist"):
    st.markdown("""
    <ul style="list-style-type:none;">
        <li><input type="checkbox"> Fuel sample(5/5/3) and fuel quantity</li>
        <li><input type="checkbox"> Oil level</li>
        <li><input type="checkbox"> Electrics, all lights and pitot heat, flaps and annunciator panel</li>
        <li><input type="checkbox"> Left tire, brake, flap, aileron</li>
        <li><input type="checkbox"> Baggage</li>
        <li><input type="checkbox"> Left horizontal stabilizer, elevator</li>
        <li><input type="checkbox"> Rudder</li>
        <li><input type="checkbox"> Right horizontal stabilizer, elevator</li>
        <li><input type="checkbox"> ELT</li>
        <li><input type="checkbox"> Right tire, brake, flap, aileron</li>
        <li><input type="checkbox"> Right leading edge</li>
        <li><input type="checkbox"> Right cabin vent ports</li>
        <li><input type="checkbox"> Exhaust</li>
        <li><input type="checkbox"> Nose wheel, oleo, shimmy damper</li>
        <li><input type="checkbox"> Propeller blade, cone</li>
        <li><input type="checkbox"> Alternator belt, air intake, no animals inside engine compartment</li>
        <li><input type="checkbox"> Static port</li>
        <li><input type="checkbox"> Left cabin vent ports</li>
        <li><input type="checkbox"> Pitot tube</li>
        <li><input type="checkbox"> Stall horn</li>
        <li><input type="checkbox"> Fuel vent</li>
        <li><input type="checkbox"> Left leading edge</li>
    </ul>
    """, unsafe_allow_html=True)

st.header(":scales: C-172S WEIGHT AND BALANCE SHEET", divider="rainbow")
aircraft = st.selectbox("Aircraft", ["C-FAQA", "C-FMNB", "C-FCAU"])
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

aircraft_poh = {
        "C-FAQA": {"normal": {"col1": [35,35,41,47.1,47.1], "col2": [0,1980,2580,2580,0]}, "utility": {"col1": [35,35,37.5,40.5,40.5], "col2": [0,1980,2200,2200,0]}},
        "C-FMNB": {"normal": {"col1": [35,35,41,47.1,47.1], "col2": [0,1980,2580,2580,0]}, "utility": {"col1": [35,35,37.5,40.5,40.5], "col2": [0,1980,2200,2200,0]}},
        "C-FCAU": {"normal": {"col1": [35,35,41,47.1,47.1], "col2": [0,1980,2580,2580,0]}, "utility": {"col1": [35,35,37.5,40.5,40.5], "col2": [0,1980,2200,2200,0]}},
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
                # step=1,
                # format="%d lb(s)",
                # width="medium",
                required=True,
            ),
            "arm": st.column_config.NumberColumn(
                "ARM(in)",
                help="Arm in in",
                min_value=0,
                max_value=200,
                # step=1,
                # format="%.2f",
                # width="medium",
                required=True,
            ),
            "moment": st.column_config.NumberColumn(
                "MOMENT",
                help="MOMENT",
                # min_value=0,
                # max_value=200,
                # step=1,
                # format="%.2f",
                # width="medium",
                required=True,
            )
            }
        )

import numpy as np

chart_data = pd.DataFrame(
   {
       "col1": np.array(aircraft_poh[aircraft]['normal']['col1'] + aircraft_poh[aircraft]['utility']['col1'] + [zero_fuel_weight['arm'], landing_weight['arm'], take_off_weight['arm']]),
       "col2": np.array(aircraft_poh[aircraft]['normal']['col2'] + aircraft_poh[aircraft]['utility']['col2'] + [zero_fuel_weight['weight'], landing_weight['weight'], take_off_weight['weight']]),
       "col3": np.array(['Normal'] * 5 + ['Utility'] * 5 + ['W&B'] * 3)
   }
)

arr = np.random.normal(1, 1, size=100)
# plt.style.use("Solarize_Light2")
# plt.style.use(['bmh'])
plt.style.use('https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-light.mplstyle')
fig, ax = plt.subplots()

for category, group_data in chart_data.groupby('col3'):
    ax.plot(group_data['col1'], group_data['col2'], marker='o', label=category)

lower_bound_lbs = 1500
ax.set_ylim(lower_bound_lbs, max(chart_data['col2']) * 1.05)  # setting the upper limit to 10% above the max value

ax2 = ax.twinx()
ax2.set_ylabel('LOADED AIRPLANE WEIGHT (KILOGRAMS)')

lbs_to_kg = 0.453592
ax2.set_ylim(ax.get_ylim()[0] * lbs_to_kg, ax.get_ylim()[1] * lbs_to_kg)

# Create a secondary x-axis at the top for millimeters
ax3 = ax.twiny()
ax3.set_xlabel('Center of Gravity Location (millimeters aft of datum)')

# Function to convert inches to millimeters
def inches_to_mm(x):
    return x * 25.4

# Setting the limits for the top x-axis based on the bottom x-axis limits converted to millimeters
ax3.set_xlim(inches_to_mm(ax.get_xlim()[0]), inches_to_mm(ax.get_xlim()[1]))

# ax.set_title('C.G. LOCATION ')
ax.set_xlabel('AIRPLANE C.G. LOCATION - INCHES AFT OF DATUM (STA. 0.0)')
ax.set_ylabel('LOADED AIRPLANE WEIGHT (POUNDS)')
ax.legend()
ax.grid(True)
ax2.grid(True, linestyle='--')
ax3.grid(True, linestyle='--')

st.pyplot(fig)

st.header("Appendix", divider="rainbow")
with st.expander("TAKE OFF BRIFING"):
    st.markdown("""
* Wind is from 010 degree at 5 knots.
* We will use runway 01.
* We will perform a normal take off.
* The calls on the roll will be "Power full, gauges green, airspeed live", and we will rotate at 55 knots.
* The decision points will be Bravo

Malfunction handling
* Any malfunction before take off, I will close the throttle, apply maximum braking and stop on the runway.
* Any engine fire or failure after take off below circuit altitude, I will close the throttle and land straight ahead.
* Any engine fire or failure above circuit altitude, I will turn back and land on the airport surface.

* Any questions?
    """)

with st.expander("CYXX AERODROM CHART"):
    st.image("images/CYXX.jpg")

with st.expander("UNDERSTANDING METAR AND TAF"):
    st.image("images/Understanding-METAR-and-TAF-p1.jpg")
    st.image("images/Understanding-METAR-and-TAF-p2.jpg")
