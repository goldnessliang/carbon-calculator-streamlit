import streamlit as st
import pandas as pd
import plotly.express as px # Import Plotly Express

# --- Configuration ---
st.set_page_config(page_title="Carbon Footprint Calculator", layout="centered")

# --- Emission Factors (Approximations - adjust as needed) ---
# ... (Emission factors remain the same) ...
EMISSION_FACTORS_TRANSPORT = { # Shortened for brevity
    "Petrol Car": 0.17, "Diesel Car": 0.16, "Electric Car (Avg Grid)": 0.05,
    "Motorbike": 0.10, "Bus": 0.08, "Train": 0.04,
    "Short-haul Flight (<3 hours)": 250, "Long-haul Flight (>3 hours)": 1800,
}
EMISSION_FACTORS_HOME = { # Shortened for brevity
    "Electricity (kWh)": 0.23, "Natural Gas (kWh)": 0.18,
    "Heating Oil (litre)": 2.5, "LPG (litre)": 1.5, "Propane (litre)": 1.5,
}
EMISSION_FACTORS_DIET = { # Shortened for brevity
    "High Meat Eater": 3300, "Medium Meat Eater": 2500, "Low Meat Eater": 1900,
    "Vegetarian": 1700, "Vegan": 1500,
}

# --- Helper Functions ---
# ... (Calculation functions remain the same) ...
def calculate_transport_emissions(inputs):
    total_emissions = 0
    if inputs.get('use_car', False):
        distance_km = inputs.get('car_distance', 0) * (52 if inputs.get('car_distance_freq') == 'Week' else 12 if inputs.get('car_distance_freq') == 'Month' else 1)
        total_emissions += distance_km * EMISSION_FACTORS_TRANSPORT.get(inputs.get('car_fuel_type'), 0)
    if inputs.get('use_motorbike', False):
        distance_km = inputs.get('motorbike_distance', 0) * (52 if inputs.get('motorbike_distance_freq') == 'Week' else 12 if inputs.get('motorbike_distance_freq') == 'Month' else 1)
        total_emissions += distance_km * EMISSION_FACTORS_TRANSPORT.get("Motorbike", 0)
    bus_dist_km = inputs.get('bus_distance', 0) * (52 if inputs.get('bus_distance_freq') == 'Week' else 12 if inputs.get('bus_distance_freq') == 'Month' else 1)
    train_dist_km = inputs.get('train_distance', 0) * (52 if inputs.get('train_distance_freq') == 'Week' else 12 if inputs.get('train_distance_freq') == 'Month' else 1)
    total_emissions += bus_dist_km * EMISSION_FACTORS_TRANSPORT.get("Bus", 0)
    total_emissions += train_dist_km * EMISSION_FACTORS_TRANSPORT.get("Train", 0)
    total_emissions += inputs.get('flights_short', 0) * EMISSION_FACTORS_TRANSPORT.get("Short-haul Flight (<3 hours)", 0)
    total_emissions += inputs.get('flights_long', 0) * EMISSION_FACTORS_TRANSPORT.get("Long-haul Flight (>3 hours)", 0)
    return total_emissions

def calculate_home_emissions(inputs):
    total_emissions = 0
    total_emissions += inputs.get('electricity_usage', 0) * 12 * EMISSION_FACTORS_HOME.get("Electricity (kWh)", 0)
    if inputs.get('use_nat_gas', False):
        total_emissions += inputs.get('nat_gas_usage', 0) * 12 * EMISSION_FACTORS_HOME.get("Natural Gas (kWh)", 0)
    if inputs.get('use_heating_oil', False):
         total_emissions += inputs.get('heating_oil_usage', 0) * 12 * EMISSION_FACTORS_HOME.get("Heating Oil (litre)", 0)
    if inputs.get('use_lpg', False):
        total_emissions += inputs.get('lpg_usage', 0) * 12 * EMISSION_FACTORS_HOME.get("LPG (litre)", 0)
    return total_emissions

def calculate_diet_emissions(diet_type):
    return EMISSION_FACTORS_DIET.get(diet_type, 0)


# --- Streamlit App Layout ---
st.title("🌍 Personal Carbon Footprint Calculator")
st.markdown("""
Welcome! This tool helps you estimate your annual carbon footprint based on your lifestyle.
Enter your details below.

**Disclaimer:** This calculator provides *estimates* based on average data. Actual emissions can vary significantly depending on your specific location, vehicle, appliances, and other factors. The electricity grid emission factor used is based on the UK average (approx. 0.23 kg CO2e/kWh) - this is a major variable globally.
""")

# --- Input Sections ---
user_inputs = {}
# ... (Input sections remain the same - Transportation, Home Energy, Diet) ...
# --- Transportation ---
st.header("🚗 Transportation")
col1, col2 = st.columns(2)
with col1:
    user_inputs['use_car'] = st.checkbox("Do you use a car regularly?")
    if user_inputs['use_car']:
        user_inputs['car_distance'] = st.number_input("Distance driven", min_value=0, value=150, step=10)
        user_inputs['car_distance_freq'] = st.selectbox("Distance Frequency", ('Week', 'Month', 'Year'), key='car_freq')
        user_inputs['car_fuel_type'] = st.selectbox("Car Fuel Type", list(EMISSION_FACTORS_TRANSPORT.keys())[0:3])
with col2:
    user_inputs['use_motorbike'] = st.checkbox("Do you use a motorbike regularly?")
    if user_inputs['use_motorbike']:
        user_inputs['motorbike_distance'] = st.number_input("Motorbike distance driven", min_value=0, value=50, step=10)
        user_inputs['motorbike_distance_freq'] = st.selectbox("Distance Frequency", ('Week', 'Month', 'Year'), key='bike_freq')
st.subheader("Public Transport & Flights")
col1a, col2a, col3a = st.columns(3)
with col1a:
    user_inputs['bus_distance'] = st.number_input("Bus distance", min_value=0, value=20, step=5)
    user_inputs['bus_distance_freq'] = st.selectbox("Frequency", ('Week', 'Month', 'Year'), key='bus_freq', index=0)
with col2a:
    user_inputs['train_distance'] = st.number_input("Train distance", min_value=0, value=30, step=5)
    user_inputs['train_distance_freq'] = st.selectbox("Frequency", ('Week', 'Month', 'Year'), key='train_freq', index=1)
with col3a:
    user_inputs['flights_short'] = st.number_input("Short Flights (<3h) per Year (Round Trips)", min_value=0, value=1, step=1)
    user_inputs['flights_long'] = st.number_input("Long Flights (>3h) per Year (Round Trips)", min_value=0, value=0, step=1)
# --- Home Energy ---
st.header("🏠 Home Energy")
st.caption(f"Electricity factor used: {EMISSION_FACTORS_HOME['Electricity (kWh)']} kg CO2e/kWh (UK avg.)")
col3, col4 = st.columns(2)
with col3:
    user_inputs['electricity_usage'] = st.number_input("Monthly Electricity Usage (kWh)", min_value=0.0, value=250.0, step=10.0, help="Check your electricity bill.")
with col4:
    st.write("Other Heating Fuels (Monthly Usage):")
    user_inputs['use_nat_gas'] = st.checkbox("Natural Gas")
    if user_inputs['use_nat_gas']:
        user_inputs['nat_gas_usage'] = st.number_input("Natural Gas (kWh)", min_value=0.0, value=800.0, step=50.0, help="Check bill (often in kWh, sometimes m³ or therms - conversion needed)")
    user_inputs['use_heating_oil'] = st.checkbox("Heating Oil")
    if user_inputs['use_heating_oil']:
        user_inputs['heating_oil_usage'] = st.number_input("Heating Oil (litres)", min_value=0.0, value=50.0, step=10.0)
    user_inputs['use_lpg'] = st.checkbox("LPG/Propane")
    if user_inputs['use_lpg']:
        user_inputs['lpg_usage'] = st.number_input("LPG/Propane (litres)", min_value=0.0, value=20.0, step=5.0)
# --- Diet ---
st.header("🍔 Diet")
user_inputs['diet_type'] = st.selectbox("Describe your diet:", list(EMISSION_FACTORS_DIET.keys()))


# --- Calculation ---
if st.button("Calculate My Footprint"):

    # Calculate emissions for each category
    transport_emissions = calculate_transport_emissions(user_inputs)
    home_emissions = calculate_home_emissions(user_inputs)
    diet_emissions = calculate_diet_emissions(user_inputs.get('diet_type'))

    # Calculate total emissions
    total_emissions_kg = transport_emissions + home_emissions + diet_emissions
    total_emissions_tonnes = total_emissions_kg / 1000

# --- Display Results ---
    st.header("📊 Your Estimated Carbon Footprint")
    st.metric(label="Total Annual Emissions", value=f"{total_emissions_tonnes:.2f} tonnes CO2e")
    st.markdown("---")

    # --- Stacked Bar Chart Section ---
    st.subheader("Breakdown by Category:")

    # Prepare data for Plotly stacked bar chart
    emissions_data = {
        'Category': ['Transportation', 'Home Energy', 'Diet'],
        'Emissions (tonnes CO2e)': [
            round(transport_emissions / 1000, 2),
            round(home_emissions / 1000, 2),
            round(diet_emissions / 1000, 2)
        ],
        'Footprint': [''] * 3 # Use empty string or just a single space if needed
    }
    df_emissions = pd.DataFrame(emissions_data)

    # Create the stacked horizontal bar chart using Plotly Express
    fig = px.bar(df_emissions,
                 x='Emissions (tonnes CO2e)',
                 y='Footprint',
                 color='Category',
                 orientation='h',
                 text='Emissions (tonnes CO2e)',
                 labels={'Emissions (tonnes CO2e)': 'Annual Emissions (tonnes CO2e)'},
                 height=200 # Adjusted height slightly
                )

    # Improve text label formatting and position
    fig.update_traces(texttemplate='%{x:.2f} t', textposition='inside', insidetextanchor='middle')

    # Customize layout: hide y-axis ticks/title, center legend, adjust margins
    fig.update_layout(
        yaxis=dict(showticklabels=False), # <-- Hide Y-axis tick labels ("Your Footprint")
        yaxis_title="",                   # <-- Ensure Y-axis title is empty
        xaxis_title="Annual Emissions (tonnes CO2e)",
        legend_title_text='',
        legend=dict(
            orientation="h",    # Horizontal legend
            yanchor="bottom",   # Anchor legend at its bottom
            y=1.02,             # Position legend slightly above the chart plot area
            xanchor="center",   # <-- Anchor legend at its center
            x=0.5               # <-- Position legend horizontally at the center
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        bargap=0.1
    )

    # --- MODIFICATION HERE ---
    # Display the Plotly chart in Streamlit, hiding the modebar
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={'displayModeBar': False} # <-- Hide the modebar
    )
    # --- END MODIFICATION ---


    # --- Comparison & Tips ---
    st.subheader("💡 Context & Reduction Tips")
    # ... (rest of the comparison and tips section remains the same) ...
    uk_avg = 5.5
    us_avg = 14.9
    world_avg = 4.7

    if total_emissions_tonnes > us_avg:
        st.warning(f"Your footprint ({total_emissions_tonnes:.1f} t) is significantly higher than the US average ({us_avg:.1f} t).")
    elif total_emissions_tonnes > uk_avg:
        st.warning(f"Your footprint ({total_emissions_tonnes:.1f} t) is higher than the UK average ({uk_avg:.1f} t). Consider areas for reduction.")
    elif total_emissions_tonnes > world_avg:
        st.info(f"Your footprint ({total_emissions_tonnes:.1f} t) is higher than the global average ({world_avg:.1f} t).")
    else:
        st.success(f"Your footprint ({total_emissions_tonnes:.1f} t) is below the global average ({world_avg:.1f} t). Keep up the good work!")

    st.markdown(f"""
    *   **Average Footprints (Tonnes CO2e per capita, consumption-based estimates):**
        *   World: ~{world_avg:.1f} tonnes
        *   UK: ~{uk_avg:.1f} tonnes
        *   USA: ~{us_avg:.1f} tonnes

    *   **Tips for Reduction:**
        *   **Transportation:** Drive less, walk/cycle more, use public transport, consider carpooling or an EV for your next vehicle, fly less often or choose more direct routes.
        *   **Home Energy:** Improve insulation, switch to energy-efficient appliances (LEDs), lower thermostat slightly, consider renewable energy tariffs or installing solar panels, use less hot water.
        *   **Diet:** Reduce consumption of red meat (beef, lamb) and dairy, opt for more plant-based meals (vegetables, legumes, grains). Eating local and seasonal food can also help.
        *   **Other:** Reduce consumption, buy durable goods, repair items, recycle properly, advocate for systemic change.
    """)


st.markdown("---")
st.caption("Calculator by [Your Name/Organization] | Emission factors are estimates.")
