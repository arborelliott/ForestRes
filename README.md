# Urban Forest Climate Change Vulnerability
Urban Forest Vulnerability


This python script analyzes a tree inventory imported by the user and compares it to an established database of tree species climate change vulnerability in order to report a summary of the inventory vulnerability. 

Source: Lewis, D., Danielle, P. (1991). <i>CHICAGO WILDERNESS REGION URBAN FOREST VULNERABILITY ASSESSMENT AND SYNTHESIS: A Report from the Urban Forestry Climate Change Response Framework Chicago Wilderness Pilot Project</i>. www.nrs.fs.fed.us

The Script will first join the imported inventory and the vulnerability index based on the latin name of species. A count of successfully and unsuccessfully merged tree species will be given. This allows the user to understand what species were present in the inventory, but not in the vulnerability index. This could be due to the species not being present in the index, or a difference in spelling of the latin name. 

Next a summary of the overall vulnerability of trees present in the inventory will be generated, this includes a table summary, as well as a bar and pie chart of the percentage of the inventory in the high - low categories.  






*The user will need to complete a series of steps to run this script.*

1. Fill out setup.json in a text editor, this includes the following variables which are based on the CSV and region that the inventory is from. Below features Syracuse NY as an example: 
    "CSV":"Syr Inventory.csv",
	"latin_name":"Sci_Name",
    "common_name":"Common_Name",
    "size":"DBH",
    "strata":"Area",
	"state_num":"36",
	"co_name":"Onondaga"

This JSON file allows the script to know where to search within the inventory for certain attributes. Fill out the second set of quotes with the information specific to your CSV and it's column headers.
EX: if the latin name column of your inventory is "l_name", then you would fill out: "latin_name":"l_name",



Table: [Vulnerability Summary](ov_summary.txt)

![Vulnerability Bar Chart](vuln_bar.png)