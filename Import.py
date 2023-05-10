# -*- coding: utf-8 -*-
"""
@author: Jordan

Other ideas:
Compare species distribution to 10/20/30 rule
match inv species to vulnerable sp key
"""

import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
from tabulate import tabulate

#%% Importing Inventory

#json translates inventory CSV column names to script
import json

info = json.load(open('setup.json'))

CSV = info['CSV']
latin = info['latin_name']
size = info['size']
strata = info['strata']
state_num = info['state_num'] #This would optimally be changed to state name for ease of use
co_name = info['co_name']

# import Inventory and vulnerability CSV
inv = pd.read_csv(CSV)
vuln = pd.read_csv('SpVuln_Index.csv', encoding = 'unicode_escape')


#%% Formatting data

# rename vuln column names to match inv
inv = inv.rename(columns={latin:'Latin Name'})
inv = inv.rename(columns={strata:'strata'})

# Merge inv and vuln based on latin_name column
vinv = pd.merge(inv, vuln, on='Latin Name', how='left',  indicator=True)

# Count of rows with 'both' in column _merge
both_count = (vinv['_merge'] == 'both').sum()
print("\nTrees successfully merged:", both_count)

# Count of rows mis-matched
left_count = (vinv['_merge'] == 'left_only').sum()
print("\nTrees not merged:", left_count)

# show which species did not merge
left_only_df = vinv[vinv['_merge'] == 'left_only']
failed_ct = left_only_df['Latin Name'].value_counts()
failed_ct = pd.DataFrame({'Species':failed_ct.index, 'Count':failed_ct.values})

# Generate failed_ct.txt
with open('output/failed_ct.txt', 'w') as f:
    f.write(tabulate(failed_ct, headers = 'keys',showindex=False))

# drop _merge column
vinv = vinv.drop(columns=['_merge'])


#%% Summary of Inventory Vulnerability

# Summary of inventory vulnerability: Count/Pct
ov_sum = vinv.groupby('Overall vulnerability')['Latin Name'].count()
ov_sum_percent = round(ov_sum/len(vinv)*100, 1)
ov_summary = pd.DataFrame({'Overall vulnerability':ov_sum.index, 'Count':ov_sum.values, 'Percentage':ov_sum_percent.values})

# Generate Ov_summary.txt
with open('output/ov_summary.txt', 'w') as f:
    f.write(tabulate(ov_summary, headers = 'keys',showindex=False))

# Summary of latin name vulnerability/Count
latin_sum = vinv.groupby(['Latin Name', 'Overall vulnerability']).size().reset_index(name='count')
latin_sum = latin_sum.sort_values('count',ascending = False)
latin_sum50 = latin_sum[latin_sum['count'] > 50]

# Generate latin_sum50.txt
with open('output/latin_sum50.txt', 'w') as f:
    f.write(tabulate(latin_sum50, headers = 'keys',showindex=False))
    

#%% Create bar chart
fig, ax = plt.subplots()
ov_sum_percent.plot(kind='bar', ax=ax)

# Set chart title and axis labels
ax.set_title('Tree Vulnerability Levels')
ax.set_xlabel('Vulnerability Level')
ax.set_ylabel('Percentage of Trees')

plt.savefig('output/vuln_bar.png')


#%% Pie Chart

fig, ax = plt.subplots()
ov_sum_percent.plot(kind='pie', ax=ax, autopct='%1.0f%%')

# Set chart title
ax.set_title('Tree Vulnerability Levels')
ax.set_ylabel('')

plt.savefig('output/vuln_pie.png')


#%% Species Origins

# Group vinv by Overall vuln, count freqency of Latin Name within each vuln category
or_sum = vinv.groupby('Origin')['Latin Name'].count()
print("\nSummary of Species origin:\n", or_sum)

# Convert counts to percentages
percentages = or_sum / len(vinv) * 100
print("\nPercentage summary of species origin:\n", round(percentages,0))

origin = pd.DataFrame({'Species':or_sum.index, 'Count':or_sum.values, 'Percentage':percentages.values})

with open('output/origin.txt', 'w') as f:
    f.write(tabulate(origin, headers = 'keys',showindex=False))


#%% Create Map

geodata = gpd.read_file('cb_2019_us_county_500k.zip')

# Filter down to state specified in JSON
geodata = geodata.query("STATEFP == '" + str(state_num) + "'")
geodata = geodata.query("NAME == '" + str(co_name) + "'")

geodata.to_file('output/county.gpkg')

#%% Generate GPKG of tree locations

# Read in lat/long columns from vinv
points = [Point(xy) for xy in zip(vinv['Longitude'], vinv['Latitude'])]

# Create GeoDF from points
gdf = gpd.GeoDataFrame(vinv, geometry=points)

# Set CRS of GeoDF to EPSG 4326
gdf.crs = 'EPSG:4326'

# Save GeoDF as geopackage file
gdf.to_file('output/tree_locations.gpkg')
