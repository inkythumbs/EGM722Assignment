import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
#pd.set_option('display.max_colwidth', 175)
import folium


def monument_finder(pcode):
    """
    This function takes a list of English postcodes and a list of English scheduled monuments
    and returns the nearest 5 mounuments to the centre point of the postcode.

    Args:
        pcode: First half of any English postcode, as a string (eg everything that comes before the gap,
        eg "NE47 P22" is written as "NE47")

    Returns: class 'pandas.core.series.Series'

    """
    monuments = gpd.read_file('Scheduled Monuments\\Monuments2.shp')
    monuments.to_crs(epsg=27700, inplace=True)
    postcodes = pd.read_csv('englishpostcodes3.csv')
    postcodes['eastings'] = pd.to_numeric(postcodes['eastings'], errors='coerce')
    postcodes['northings'] = pd.to_numeric(postcodes['northings'], errors='coerce')
    # postcodes.dropna(inplace=True)
    geometry = [Point(xy) for xy in zip(postcodes['eastings'], postcodes['northings'])]
    postcodes['geometry'] = geometry
    postcodes = gpd.GeoDataFrame(postcodes)
    postcodes.set_crs(epsg=27700, inplace=True)
    postcode = postcodes.loc[postcodes['postcode'] == pcode, 'geometry'].values[0]
    monuments['distance'] = monuments['geometry'].distance(postcode)
    monuments.sort_values(by='distance', ascending=True, inplace=True)
    monuments.reset_index(inplace=True)
    # print("the type of object my function returns is:", type(monuments['Name'].head()))
    return monuments.head()


def monument_finder_map(pcode):
    """
    This function refreshes the map so that only the new outputs are displayed.

    Args:
        pcode: First half of any English postcode, as a string (eg everything that comes before the gap,
        eg "NE47 P22" is written as "NE47")

    Returns: class 'pandas.core.series.Series'

    """
    nearest_monument = monument_finder(pcode)
    my_map = folium.Map(location=[52.4776, 1.8944], zoom_start=6)
    for _, r in nearest_monument.to_crs(epsg=4326).iterrows():
        centroid = gpd.GeoSeries(r['geometry']).set_crs(epsg=4326).to_crs(epsg=27700).centroid
        centroid = gpd.GeoSeries(centroid).set_crs(epsg=27700).to_crs(epsg=4326)
        # adding the centroid to the map,and ensuring it displays at the right scale
        folium.Marker(location=[centroid.y, centroid.x], popup=r['Name']).add_to(my_map)
        # Project to [insert right crs)] projected crs
        nearest_monument = nearest_monument.to_crs(epsg=2263)
        # Access the centroid attribute of each polygon
        nearest_monument['centroid'] = nearest_monument.centroid
        # geometry (active) column
        nearest_monument = nearest_monument.to_crs(epsg=4326)
        # Centroid column
        nearest_monument['centroid'] = nearest_monument['centroid'].to_crs(epsg=4326)

        nearest_monument.head()
    return my_map