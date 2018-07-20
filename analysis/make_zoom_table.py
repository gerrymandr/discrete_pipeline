import geopandas as gpd
import pandas as pd

"""Makes the zoom table comparing the 4 different zoom levels of shapefiles. 
The list of cartographic boundary files from most to least granular is: ["cb500k", "cb5m", "cb20m"]. 
Tigerline and cb500k differ mostly in their treatment of water. 
The output also includes the land area and water area for each shapefile and corresponding rankings"""


# Load in 4 data tables, used tracts but tract = block group for continuous
files = ["tigerline", "cb500k", "cb5m", "cb20m"]
tiger = pd.read_csv("./tables_merged/tigerline_tract.csv", dtype={"geoid": str})
tiger = tiger.rename(columns={'c_area': 'tiger_c_area', 'c_perim': 'tiger_c_perim',
                              'c_a/p^2': 'tiger_c_4pi*a/p^2', 'rank_c_a/p^2': 'tiger_rank_c_4pi*a/p^2'})
cb500 = pd.read_csv("./tables_merged/cb500k_tract.csv", dtype={"geoid": str})
cb500 = cb500.rename(columns={'c_area': '500k_c_area', 'c_perim': '500k_c_perim',
                              'c_a/p^2': '500k_c_4pi*a/p^2', 'rank_c_a/p^2': '500k_rank_c_4pi*a/p^2'})
cb5 = pd.read_csv("./tables_merged/cb5m_tract.csv", dtype={"geoid": str})
cb5 = cb5.rename(columns={'c_area': '5m_c_area', 'c_perim': '5m_c_perim',
                              'c_a/p^2': '5m_c_4pi*a/p^2', 'rank_c_a/p^2': '5m_rank_c_4pi*a/p^2'})
cb20 = pd.read_csv("./tables_merged/cb20m_tract.csv", dtype={"geoid": str})
cb20 = cb20.rename(columns={'c_area': '20m_c_area', 'c_perim': '20m_c_perim',
                              'c_a/p^2': '20m_c_4pi*a/p^2', 'rank_c_a/p^2': '20m_rank_c_4pi*a/p^2'})

# Merge 4 data tables
df = tiger.merge(cb500,left_on = "geoid", right_on = "geoid").merge(
    cb5,left_on = "geoid", right_on = "geoid").merge(
    cb20, left_on = "geoid", right_on = "geoid")

# Adding state abbreviations
fips = pd.read_csv('../state_fips.txt', sep='\t', lineterminator='\n', dtype={"STATE": str, "FIP": str})
fips_dict = {}
for i, row in fips.iterrows():
    fips_dict.update({row["FIP"]:row["ABBREVIATION"]})
abbrev = []
for i in df['geoid']:
    abbrev.append(fips_dict[i[:2]])
df['state'] = abbrev

# Load in 4 district shapefiles and rename aland and awater to be unique to each
tiger_plan = gpd.GeoDataFrame.from_file(
        '../approx_unit_run/districting_plans/cd2013/tl_rd13_us_cd113.shp')
tiger_plan = tiger_plan.rename(columns={'ALAND': 'tiger_aland', 'AWATER': 'tiger_awater'})
cb500_plan = gpd.GeoDataFrame.from_file(
        '../approx_unit_run/districting_plans/cb_2013_us_cd113_500k/cb_2013_us_cd113_500k.shp')
cb500_plan = cb500_plan.rename(columns={'ALAND': 'cb500k_aland', 'AWATER': 'cb500k_awater'})
cb5_plan = gpd.GeoDataFrame.from_file(
        '../approx_unit_run/districting_plans/cb_2013_us_cd113_5m/cb_2013_us_cd113_5m.shp')
cb5_plan = cb5_plan.rename(columns={'ALAND': 'cb5m_aland', 'AWATER': 'cb5m_awater'})
cb20_plan = gpd.GeoDataFrame.from_file(
        '../approx_unit_run/districting_plans/cb_2013_us_cd113_20m/cb_2013_us_cd113_20m.shp')
cb20_plan = cb20_plan.rename(columns={'ALAND': 'cb20m_aland', 'AWATER': 'cb20m_awater'})

df.sort_values('geoid', inplace=True)

# Merge 4 shapefiles to the previously merged data table
df = df.merge(tiger_plan, left_on = "geoid", right_on = "GEOID").merge(
        cb500_plan, left_on = "geoid", right_on = "GEOID").merge(
                cb5_plan, left_on = "geoid", right_on = "GEOID").merge(
                        cb20_plan, left_on = "geoid", right_on = "GEOID")

# Add rankings of land and water
rank = []
for i in ["tiger", "cb500k", "cb5m", "cb20m"]:
    df["rank_" + i + "_aland"] = df[i + "_aland"].rank(ascending = False)
    df["rank_" + i + "_awater"] = df[i + "_awater"].rank(ascending = False)
    rank = rank + ['rank_' + i + '_aland', 'rank_' + i + '_awater']

# Reoder the columns
df = df[['geoid', 'state', 
         'tiger_rank_c_4pi*a/p^2', '500k_rank_c_4pi*a/p^2', '5m_rank_c_4pi*a/p^2', '20m_rank_c_4pi*a/p^2',
         'tiger_c_4pi*a/p^2', '500k_c_4pi*a/p^2', '5m_c_4pi*a/p^2', '20m_c_4pi*a/p^2',
         'tiger_c_perim', '500k_c_perim', '5m_c_perim', '20m_c_perim',
         'tiger_c_area', '500k_c_area', '5m_c_area', '20m_c_area'] + rank + [
         'tiger_aland', 'tiger_awater',
         'cb500k_aland', 'cb500k_awater',
         'cb5m_aland', 'cb5m_awater',
         'cb20m_aland', 'cb20m_awater']]

# Write new table to CSV
df.to_csv("./zoom_table.csv")  
