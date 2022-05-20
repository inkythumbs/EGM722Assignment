import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
#pd.set_option('display.max_colwidth', 175)
import folium


def monument_finder(pcode):
    """
    This function takes a list of English postcodes and a list of English scheduled monuments
    and returns the nearest 5 monuments to the centre point of the postcode.

    Args:
        pcode: First half of any English postcode, as a string (eg "NE47 P22" is written as "NE47")

    Returns: class 'pandas.core.series.Series'

    """
    #uses geopandas function to read shapefile
    monuments = gpd.read_file('Scheduled Monuments\\Monuments2.shp')
    #projects shapefile to EPSG 27700
    monuments.to_crs(epsg=27700, inplace=True)
    #uses pandas to read csv file
    postcodes = pd.read_csv('englishpostcodes3.csv')
    #uses pandas 'to_numeric' method to convert the eastings and northings values to numeric types
    postcodes['eastings'] = pd.to_numeric(postcodes['eastings'], errors='coerce')
    postcodes['northings'] = pd.to_numeric(postcodes['northings'], errors='coerce')
    # creates a point geometry column, based on the values in the eastings and northings columns
    geometry = [Point(xy) for xy in zip(postcodes['eastings'], postcodes['northings'])]
    postcodes['geometry'] = geometry
    # converts file into a geodataframe
    postcodes = gpd.GeoDataFrame(postcodes)
    # projects geometry to EPSG 27700
    postcodes.set_crs(epsg=27700, inplace=True)
    # associates a given postcode with its geometry
    postcode = postcodes.loc[postcodes['postcode'] == pcode, 'geometry'].values[0]
    # calculates distance from each monument to a given postcode
    monuments['distance'] = monuments['geometry'].distance(postcode)
    # sorts monuments by ascending distance from a given postcode
    monuments.sort_values(by='distance', ascending=True, inplace=True)
    # resets the index field so the list of sorted monuments starts at 0 (rather than using previous index numbers)
    monuments.reset_index(inplace=True)
    # returns the first 5 monuments in the list
    return monuments.head()


def monument_finder_map(pcode):
    """
    This function refreshes the map so that only the new outputs are displayed each time the code is run.

    Args:
        pcode: First half of any English postcode, as a string (eg "NE47 P22" is written as "NE47")

    Returns: class 'pandas.core.series.Series'

    """
    nearest_monument = monument_finder(pcode)
    # centres the map just SE of the UK coast, at a suitable scale to ensure the whole of England is displayed
    my_map = folium.Map(location=[52.4776, 1.8944], zoom_start=6)
    for _, r in nearest_monument.to_crs(epsg=4326).iterrows():
        centroid = gpd.GeoSeries(r['geometry']).set_crs(epsg=4326).to_crs(epsg=27700).centroid
        centroid = gpd.GeoSeries(centroid).set_crs(epsg=27700).to_crs(epsg=4326)
        # adds a marker to the centroid of each monument polygon, which displays the content of the gdf's 'Name' field
        folium.Marker(location=[centroid.y, centroid.x], popup=r['Name'],
                      icon=folium.Icon(color="red", icon="info-sign")).add_to(my_map)
        # Project to [insert right crs)] projected crs
        nearest_monument = nearest_monument.to_crs(epsg=2263)
        # Access the centroid attribute of each polygon
        nearest_monument['centroid'] = nearest_monument.centroid
        nearest_monument = nearest_monument.to_crs(epsg=4326)
        nearest_monument['centroid'] = nearest_monument['centroid'].to_crs(epsg=4326)
        nearest_monument.head()
    return my_map