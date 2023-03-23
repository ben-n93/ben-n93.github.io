Title: Where are Australia's oil and gas pipelines located?
Date: 2023-03-22
Category: Blog
Tags: data-visualisation, geospatial-data

Recently I was browsing Geoscience Australia's datasets and came across
a useful [database](https://ecat.ga.gov.au/geonetwork/srv/eng/catalog.search#/metadata/147583) of *"known spatial locations of onshore and offshore 
pipelines or pipeline corridors used to transport natural gas, oil and 
other liquids within Australia’s mainland and territorial waters."*

I thought it'd be interesting to see on a map of Australia *where* these pipelines
are located:

<iframe src="existing_pipelines.html" height="500" width="750"></iframe>

Also provided in the dataset was proposed gas and oil pipelines, which you can see here:

<iframe src="proposed_pipelines.html" height="500" width="750"></iframe>

If you want to view the data used for this, you can access the aforementioned Geoscience
database. I've also saved a copy of the data to [this Github repo](https://github.com/ben-n93/australia_gas_oil_pipelines), along with
the source code for this project (more details as follows).

## How I did it

The GeoJSON files provided in Geoscience's database bundled together 
existing and proposed pipelines. 

As I knew I wanted separate maps for existing
vs proposed pipelines I used Python to parse these GeoJSON files and create new 
GeoJSON files:

``` python
import json

# Base dictionary for new GeoJSON files.
new_geojson = {"type" : "FeatureCollection", "name" : ""}

# Create new oil GeoJSON files.
with open('Oil_Pipelines_v3.geojson') as f:
    data = json.load(f)
    built_oil_pipelines = []
    proposed_oil_pipelines = []
    for pipeline in data['features']:
        if pipeline['properties']['FEATURE_TYPE'] == 'Proposed Oil pipeline':
            proposed_oil_pipelines.append(pipeline)
        elif pipeline['properties']['FEATURE_TYPE'] == 'Oil pipeline':
            built_oil_pipelines.append(pipeline)

new_geojson['name'] = 'built_oil_pipelines'
new_geojson['features'] = built_oil_pipelines
with open('existing_oil_pipelines.geojson', 'w') as f:
    json.dump(new_geojson, f)

new_geojson['name'] = 'proposed_oil_pipelines'
new_geojson['features'] = proposed_oil_pipelines
with open('proposed_oil_pipelines.geojson', 'w') as f:
    json.dump(new_geojson, f)

# Create new gas GeoJSON files.
with open('Gas_Pipelines_v3.geojson') as f:
    data = json.load(f)
    built_gas_pipelines = []
    proposed_gas_pipelines = []
    for pipeline in data['features']:
        if pipeline['properties']['FEATURE_TYPE'] == 'Proposed Gas pipeline':
            proposed_gas_pipelines.append(pipeline)
        elif pipeline['properties']['FEATURE_TYPE'] == 'Gas pipeline':
            built_gas_pipelines.append(pipeline)

new_geojson['name'] = 'built_gas_pipelines'
new_geojson['features'] = built_gas_pipelines
with open('existing_gas_pipelines.geojson', 'w') as f:
    json.dump(new_geojson, f)

new_geojson['name'] = 'proposed_gas_pipelines'
new_geojson['features'] = proposed_gas_pipelines
with open('proposed_gas_pipelines.geojson', 'w') as f:
    json.dump(new_geojson, f)
```

I then used [Folium](https://python-visualization.github.io/folium/), a fantastic Python library for creating interactive maps.

As you can see, a GeoJSON file is required for each layer in a Folium map, hence the
data cleaning/wrangling I demonstrated earlier:

```python
import folium

# Existing pipelines map.
m = folium.Map(location=[-22.575567970590456, 133.41701195],zoom_start=4)

folium.GeoJson(data='./existing_gas_pipelines.geojson', name="Existing gas pipelines", style_function= lambda feature: {
        'color': 'orange'
    },tooltip=folium.GeoJsonTooltip(fields=['NAME', 'FEATURE_TYPE'])).add_to(m)

folium.GeoJson(data='./existing_oil_pipelines.geojson', name="Existing oil pipelines", style_function=lambda feature: {
        'color': 'red'
    }, tooltip=folium.GeoJsonTooltip(fields=['NAME', 'FEATURE_TYPE'])).add_to(m)

folium.LayerControl(collapsed=False).add_to(m)
m.save("./existing_pipelines.html")

# Proposed pipelines map.
m = folium.Map(location=[-22.575567970590456, 133.41701195],zoom_start=4)

folium.GeoJson(data='./proposed_gas_pipelines.geojson', name="Proposed gas pipelines", style_function= lambda feature: {
        'color': 'orange', 
    },tooltip=folium.GeoJsonTooltip(fields=['NAME', 'FEATURE_TYPE'])).add_to(m)

folium.GeoJson(data='./proposed_oil_pipelines.geojson', name="Proposed oil pipelines", style_function=lambda feature: {
        'color': 'red', 'dashArray': '5, 5'
    }, tooltip=folium.GeoJsonTooltip(fields=['NAME', 'FEATURE_TYPE'])).add_to(m)

folium.LayerControl(collapsed=False).add_to(m)
m.save("./proposed_pipelines.html")
```