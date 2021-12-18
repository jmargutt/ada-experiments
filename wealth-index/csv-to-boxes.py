import pandas as pd
import numpy as np
import math
import rasterio
from rasterio.transform import from_origin
import os
from tqdm import tqdm
from scipy.interpolate import griddata
import geopandas as gpd
from shapely.geometry import box


def meters_to_longitude(meters, latitude):
    """ convert meters to decimal degrees, based on latitude
    World circumference measured around the equator is 40,075.017 km (source: wikipedia)
    40075.017 / 360 = 111.319491667 km/deg
    """
    return meters / (111.319491667 * 1000 * math.cos(latitude * (math.pi / 180)))


def meters_to_latitude(meters):
    """ convert meters to decimal degrees, based on latitude
    World circumference measured around the equator is 40,075.017 km (source: wikipedia)
    40075.017 / 360 = 111.319491667 km/deg
    """
    return meters / (111.132952778 * 1000)


def csv_to_raster(input_csv, output_raster, resolution=2400):
    """ convert csv file to raster """

    # read csv
    df = pd.read_csv(input_csv)

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))
    gdf.to_file(output_raster.replace('.tif', '._points.gpkg'), driver='GPKG')

    for ix, row in gdf.iterrows():
        lon_size = meters_to_longitude(resolution, row['latitude'])
        lat_size = meters_to_latitude(resolution)
        gdf.at[ix, 'geometry'] = box(row['longitude']-lon_size*0.5, row['latitude']-lat_size*0.5,
                                     row['longitude']+lon_size*0.5, row['latitude']+lat_size*0.5)
    gdf.to_file(output_raster.replace('.tif', '._squares.gpkg'), driver='GPKG')


if __name__ == "__main__":

    input_dir = "relative-wealth-index-april-2021"
    output_dir = input_dir+"-geotiff"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    dist_all = pd.DataFrame()
    for file in os.listdir(input_dir):
        print(f"processing {file}")
        input_filepath = os.path.join(input_dir, file)
        output_filepath = os.path.join(output_dir, file.replace('.csv', '.tif'))
        csv_to_raster(input_filepath, output_filepath)