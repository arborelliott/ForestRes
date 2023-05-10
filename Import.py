# -*- coding: utf-8 -*-
"""

@author: Jordan

Other ideas: Map of trees
Compare species distribution to 10/20/30 rule
match inv species to vulnerable sp key

vulnerability by strata

"""

import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point


#from fpdf import FPDF

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

# print records merged
#print(vinv['_merge'].value_counts())

# Count of rows with 'both' in column _merge
both_count = (vinv['_merge'] == 'both').sum()
print("\nTrees successfully merged:", both_count)

# Count of rows mis-matched
left_count = (vinv['_merge'] == 'left_only').sum()
print("\nTrees not merged:", left_count)

# show which species did not merge
left_only_df = vinv[vinv['_merge'] == 'left_only']
failed_ct = left_only_df['Latin Name'].value_counts()
print("Species which failed to merge:\n", failed_ct)
# generate CSV of mismatched species
failed_ct.to_csv('mismatch.csv')

# drop _merge
vinv = vinv.drop(columns=['_merge'])

#%% Summary of Inventory Vulnerability

# Group vinv by Overall vuln, count freqency of Latin Name within each vuln category
ov_sum = vinv.groupby('Overall vulnerability')['Latin Name'].count()
print("\nSummary of Overall vulnerability:\n", ov_sum)

# Convert counts to percentages
percentages = ov_sum / len(vinv) * 100
print("\nPercentage summary of Overall vulnerability:\n", round(percentages,0))

latin_sum = vinv.groupby(['Latin Name', 'Overall vulnerability']).size().reset_index(name='count')
latin_sum = latin_sum.sort_values('count',ascending = False)
print('Most common species\n', latin_sum[latin_sum['count'] > 100])




#%% Create bar chart
fig, ax = plt.subplots()
percentages.plot(kind='bar', ax=ax)

# Set chart title and axis labels
ax.set_title('Tree Vulnerability Levels')
ax.set_xlabel('Vulnerability Level')
ax.set_ylabel('Percentage of Trees')

# Show plot
plt.show()
plt.savefig('vuln_bar.png')

#%% Pie Chart

fig, ax = plt.subplots()
percentages.plot(kind='pie', ax=ax, autopct='%1.0f%%')

# Set chart title
ax.set_title('Tree Vulnerability Levels')
ax.set_ylabel('')

# Show plot
plt.savefig('vuln_pie.png')
plt.show()


#%% Species Origins

# Group vinv by Overall vuln, count freqency of Latin Name within each vuln category
or_sum = vinv.groupby('Origin')['Latin Name'].count()
print("\nSummary of Species origin:\n", or_sum)

# Convert counts to percentages
percentages = or_sum / len(vinv) * 100
print("\nPercentage summary of species origin:\n", round(percentages,0))

#%% Create Map

geodata = gpd.read_file('cb_2019_us_county_500k.zip')

# Filter down to state specified in JSON
geodata = geodata.query("STATEFP == '" + str(state_num) + "'")
geodata = geodata.query("NAME == '" + str(co_name) + "'")

geodata.to_file('county.gpkg')

#%% Generate GPKG of tree locations

# Read in lat/long columns from vinv
points = [Point(xy) for xy in zip(vinv['Longitude'], vinv['Latitude'])]

# Create GeoDF from points
gdf = gpd.GeoDataFrame(vinv, geometry=points)

# Set CRS of GeoDF to EPSG 4326
gdf.crs = 'EPSG:4326'

# Save GeoDF as geopackage file
gdf.to_file('tree_locations.gpkg')



#%% Export to PDF Report





