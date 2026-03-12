from osgeo import osr, gdal
from osgeo_utils import gdal_merge
from pyproj import Transformer
import subprocess

gdal_merge_py = r"C:\Users\micky\anaconda3\Scripts\gdal_merge.py"

# A function to compute the bounds of multiple rasters for merging
def tif_merger(out_tif, input_tifs):
    cmd = ["python", gdal_merge_py, "-o",out_tif]+input_tifs  # + ".tif" #gdal_merge.py
    subprocess.call(cmd)

    #subprocess.call(cmd.split()+input_tifs)

def tif_clipper(out_tif, in_tif, min_lon, min_lat, max_lon, max_lat):
     """
     Clips a raster to a certain extent. Output raster will be in the same projection as the input raster.
     Latitude and Longitude points will be reprojected to this projection.

     out_tif = path of output file
     in_tif = path of input file
     min_lon, min_lat, max_lon, max_lat = minimum and maximum latitude and longitude in EPSG:4326 respectively
     """

     transformer = Transformer.from_crs("EPSG:4326", "EPSG:32616", always_xy = True)
     min_x, min_y = transformer.transform(min_lon, min_lat)
     max_x, max_y = transformer.transform(max_lon, max_lat)

     gdal.Warp(
        out_tif,
        in_tif,
        outputBounds = (min_x, min_y, max_x, max_y),
        cropToCutline = True,
        #dstnoData = 2
     )

def reproject(output_image, input_image, output_epsg, output_scale):
    gdal.Warp(
        output_image,
        input_image,
        dstSRS = output_epsg,
        xRes = output_scale,
        yRes = output_scale,
        resampleAlg = "near"
    )

from osgeo import gdal
import os
