import pandas as pd
import numpy as np
import math
import rasterio
from rasterio.transform import from_origin
import os
from tqdm import tqdm


def meters_to_longitude(meters, latitude):
    """ convert meters to decimal degrees, based on latitude
    World circumference measured around the equator is 40,075.017 km (source: wikipedia)
    40,075.017 / 360 = 111.319491667 km/deg
    """
    return meters / (111.319491667 * 1000 * math.cos(latitude * (math.pi / 180)))


def meters_to_latitude(meters):
    """ convert meters to decimal degrees, based on latitude
    World circumference measured around the poles is 40,007.863 km (source: wikipedia)
    40,007.863 / 360 = 111.132952778 km/deg
    """
    return meters / (111.132952778 * 1000)


def csv_to_raster(input_csv, output_raster, resolution=2400):
    """ convert csv file to raster, given fixed raster cell size """

    # read csv
    df = pd.read_csv(input_csv)

    # calculate raster cell size
    step_lon = meters_to_longitude(resolution, df.latitude.mean())
    step_lat = meters_to_latitude(resolution)
    # get minimum latitude and longitude
    lat_min = df.latitude.min()
    lon_min = df.longitude.min()
    # get extent in longitude and latitude
    Dlat = abs(df.latitude.max() - lat_min)
    Dlon = abs(df.longitude.max() - lon_min)
    # convert extent in number of raster cells
    size_lat = round(Dlat / step_lat) + 1
    size_lon = round(Dlon / step_lon) + 1
    # initialize empty array
    arr = np.empty((size_lat, size_lon))
    arr[:] = np.nan

    # loop over the csv file and fill the array
    for ix, row in df.iterrows():
        dlat = abs(row['latitude'] - lat_min)
        dlon = abs(row['longitude'] - lon_min)
        ilat = round((size_lat - 1) * dlat / Dlat)
        ilon = round((size_lon - 1) * dlon / Dlon)
        # correct for rasterio flip
        ilat = size_lat - ilat - 1
        arr[ilat, ilon] = row['rwi']

    # transform array into raster
    transform = from_origin(lon_min - step_lon * 0.5,
                            df.latitude.max() + step_lat * 0.5,
                            step_lon, step_lat)
    new_raster = rasterio.open(output_raster, 'w', driver='GTiff',
                               height=arr.shape[0], width=arr.shape[1],
                               count=1, dtype=str(arr.dtype),
                               crs='EPSG:4326',
                               transform=transform)
    # save raster
    new_raster.write(arr, 1)
    new_raster.close()


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