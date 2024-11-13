import pandas as pd
import plotly.express as px
import streamlit as st
import geopandas as gpd
import streamlit.components.v1 as components 
import folium
from folium import features
from branca.colormap import StepColormap
from folium.plugins import Search

st.set_page_config(page_title="DSS5201 Data visualization", layout="wide")   
st.header("This is our group's interactive visualization")

map_data = pd.read_csv("../data/data_for_map.csv")
line_data = pd.read_csv("../data/line_data.csv")


# (1) Map Visualization
world = gpd.read_file("../data/wk11_worldmap.geojson")
g = world.merge(map_data, how="left", left_on="SOVEREIGNT", right_on="Country")
g["Cumulative production"] = g["Cumulative production"].fillna(0)

# Initialize the Folium map
m = folium.Map(location=[20, 0], zoom_start=2, tiles="cartodb positron")

# Define the colormap with the custom color order
colormap = StepColormap(
    colors=[
        '#D2B48C', '#C9A66D', '#B88D00', '#D57A00', '#FF6F00',
        '#B22222', '#8B0000', '#800000', '#660000', '#800020', '#4B0000'
    ],
    index=[0, 5, 10, 50, 100, 200, 500, 650, 1000, 1300, 1468],
    vmin=5, vmax=1468
)

# Add GeoJson layer with tooltips to the map
tooltip = features.GeoJsonTooltip(
    fields=["SOVEREIGNT", "Cumulative production"],
    aliases=["Country: ", "Cumulative production (EJ): "],
    localize=True,
    sticky=True
)

# Define the highlight function (same as hover)
highlight_function = lambda feature: {
    'weight': 2,
    'color': 'black',
    'fillOpacity': 0.7
}

# Add GeoJson layer
geojson_layer = folium.GeoJson(
    g,
    style_function=lambda feature: {
        'fillColor': colormap(feature['properties']['Cumulative production']) if feature['properties']['Cumulative production'] is not None else '#d3d3d3',
        'color': 'black',
        'weight': 0.5,
        'fillOpacity': 0.9
    },
    highlight_function=highlight_function,
    tooltip=tooltip,
    control=False
).add_to(m)

# Add the colormap legend to the map
colormap.caption = 'Cumulative production (EJ)'
colormap.add_to(m)

# Add Search functionality (try to disable red circle, but there is no effect)
search = Search(
    geojson_layer,
    search_label='SOVEREIGNT',
    placeholder='Search for a country...',
    collapsed=False,
    search_zoom=2,
    use_marker=False
).add_to(m)

# Create an HTML title and subtitle for the map
title_html = '''
    <h3 align="left" style="font-size:20px; font-weight:bold;">
    Cumulative natural gas production by country, 1900-2022
    </h3>
    <p align="left" style="font-size:12px; color:gray;">
    Units are exajoules.
    </p>
'''
m.get_root().html.add_child(folium.Element(title_html))

# Save and display the map
m.save("natural_gas_production_map_with_search_no_redcircle.html")

# use streamlit to display the map
st.header("Fig 1: Cumulative Natural Gas Production by Country")
components.html(open("natural_gas_production_map_with_search_no_redcircle.html", "r", encoding="utf-8").read(), height=800)



# （2）Line Chart Visualization
st.title("Fig 2")
countries = [
    'United States', 'Russia', 'Iran', 'China', 'Canada', 'Afghanistan', 'Albania', 'Algeria', 
    'Angola', 'Argentina', 'Australia', 'Austria', 'Azerbaijan', 'Bahrain', 'Bangladesh', 
    'Barbados', 'Belarus', 'Belgium', 'Bolivia', 'Bosnia and Herzegovina', 'Brazil', 'Brunei', 
    'Bulgaria', 'Cameroon', 'Chile', 'Colombia', 'Congo', "Cote d'Ivoire", 'Croatia', 'Cuba', 
    'Czechia', 'Czechoslovakia', 'Denmark', 'East Timor', 'Ecuador', 'Egypt', 'Equatorial Guinea', 
    'France', 'Gabon', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Hungary', 'India', 'Indonesia', 
    'Iraq', 'Ireland', 'Israel', 'Italy', 'Japan', 'Jordan', 'Kazakhstan', 'Kuwait', 'Kyrgyzstan', 
    'Libya', 'Malaysia', 'Mexico', 'Moldova', 'Morocco', 'Mozambique', 'Myanmar', 'Netherlands', 
    'New Zealand', 'Nigeria', 'Norway', 'Oman', 'Pakistan', 'Papua New Guinea', 'Peru', 
    'Philippines', 'Poland', 'Qatar', 'Romania', 'Saudi Arabia', 'Senegal', 'Serbia', 'Slovakia', 
    'Slovenia', 'South Africa', 'South Korea', 'Spain', 'Switzerland', 'Syria', 'Taiwan', 
    'Tajikistan', 'Tanzania', 'Thailand', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 
    'Turkmenistan', 'USSR', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'Uzbekistan', 
    'Venezuela', 'Vietnam', 'World', 'Yemen', 'Yugoslavia'
]

selected_countries = st.multiselect("Select countries to display", countries, default =['United States', 'Russia', 'Iran', 'China', 'Canada'])

if selected_countries:
    line_data_long = line_data.melt(
        id_vars=["Year"], 
        value_vars=selected_countries, 
        var_name='Country',
        value_name='Production'
    )
    
    fig_line = px.line(
        line_data_long, 
        x="Year", 
        y="Production", 
        color="Country", 
        title="Natural Gas Production by Country (1900-2022)"
    )

    # Set x-axis interval to 10 years
    fig_line.update_xaxes(dtick=10, tickformat="%Y")

    # Add vertical lines for significant events
    events = [
        {"year": 1960, "label": "OPEC Founded"},
        {"year": 1973, "label": "1973 Oil Crisis"},
        {"year": 2008, "label": "2008 Financial Crisis"}
    ]

    for event in events:
        fig_line.add_vline(
            x=event["year"],
            line=dict(color="black", width=1, dash="dash"),
            annotation_text=event["label"],
            annotation_position="top",
            annotation=dict(font_size=10, showarrow=True, arrowhead=1)
        )

    fig_line.update_layout(width=700, height=680, title_font=dict(size=20))
    st.plotly_chart(fig_line, use_container_width=True)
    
    
# (3) Ranking Bar Chart Visualization
st.title("Fig 3")
selected_year = st.slider("Select a Year", min_value = 1900, max_value = 2022, value = 2022)

if selected_year and selected_countries:
    
    # Filter data for selected year and previous year
    selected_year_data = line_data[line_data['Year'] == selected_year][['Year'] + selected_countries]
    previous_year_data = line_data[line_data['Year'] == selected_year - 1][['Year'] + selected_countries]
    
    col1, col2 = st.columns(2)
    
    # Calculate production change
    if not previous_year_data.empty:
        production_diff = selected_year_data.iloc[0, 1:].values - previous_year_data.iloc[0, 1:].values
        gain_loss_df = pd.DataFrame({
            'Country': selected_countries,
            'Production Change': production_diff
        }).sort_values(by='Production Change', ascending=False)
        
        col1.subheader("Top Gains/Losses")
        
        top_gain = gain_loss_df.sort_values("Production Change", ascending = False).head(1)
        top_gain_name = top_gain["Country"].values[0]
        top_gain_value = top_gain["Production Change"].values[0]
        
        lowest_gain = gain_loss_df.sort_values("Production Change", ascending = True).head(1)
        lowest_gain_name = lowest_gain["Country"].values[0]
        lowest_gain_value = lowest_gain["Production Change"].values[0]
        
        col1.metric(top_gain_name, f"{top_gain_value:.2f}", f"{top_gain_value:.2f}")
        col1.metric(lowest_gain_name, f"{lowest_gain_value:.2f}", f"{lowest_gain_value:.2f}")
        
        # Add description text below the metrics
        col1.write("Gains/Losses: Countries with the highest increase or decrease in production for the selected year.")
    
    
    # bar chart
    tidy_year_data = selected_year_data.melt(id_vars=["Year"], var_name="Country", value_name="Production")
    tidy_year_data = tidy_year_data.sort_values(by="Production", ascending=False)
    
    fig_bar = px.bar(
        tidy_year_data, 
        x="Production", 
        y="Country", 
        orientation='h',
        title = f"Natural Gas Production Ranking for Selected Year",
        labels = {"Production": "Production (Billion Cubic Feet)", "Country": "Country"}
    )
    
    fig_bar.update_layout(width = 700, height = 800, title_font=dict(size=20))
    col2.plotly_chart(fig_bar, use_container_width=True)