import pandas as pd
import os
import click
import mercantile
import geopandas as gpd
from shapely.geometry import box
from pyquadkey2 import quadkey


def calculate_tile_bbox(row):
    print(row)
    qk = str(quadkey.from_geo((row['latitude'], row['longitude']), 14))
    b = mercantile.bounds(mercantile.quadkey_to_tile(qk))
    return box(b.west, b.south, b.east, b.north)


def meters_to_latitude(meters):
    """ convert meters to decimal degrees, based on latitude
    World circumference measured around the equator is 40,075.017 km (source: wikipedia)
    40075.017 / 360 = 111.319491667 km/deg
    """
    return meters / (111.132952778 * 1000)


def csv_to_raster(input_csv, output_vector):
    """ convert csv file to raster """

    # read csv
    df = pd.read_csv(input_csv)
    print(df.head())

    df['geometry'] = df.apply(calculate_tile_bbox, axis=0)
    gdf = gpd.GeoDataFrame(df, geometry=df['geometry'])
    print(gdf.head())

    gdf.to_file(output_vector, driver='GPKG')


@click.command()
@click.option('--data', default='data-input', help='input directory')
@click.option('--dest', default='data-output', help='output directory')
def convert_from_dir(data, dest):
    input_dir = data
    output_dir = dest
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in os.listdir(input_dir):
        print(f"processing {file}")
        input_filepath = os.path.join(input_dir, file)
        output_filepath = os.path.join(output_dir, file.replace('.csv', '.gpkg'))
        csv_to_raster(input_filepath, output_filepath)


if __name__ == "__main__":
    convert_from_dir()