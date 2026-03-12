from osgeo import gdal
import numpy as np

def get_inc_angle(image):
    info =gdal.Info(image)
    character = info.find('INCIDENCE_CENTER')
    inc_angle = info[character:character+24].split('=')[1]

    return inc_angle


def add_inc_angle_band(output_image, input_image, angle):
    dataset = gdal.Open(input_image, gdal.GA_ReadOnly)

    geotransform = dataset.GetGeoTransform()
    proj = dataset.GetProjection()
    xsize = dataset.RasterXSize
    ysize = dataset.RasterYSize
    nbands = dataset.RasterCount

    driver = gdal.GetDriverByName("GTiff")
    out_dataset = driver.Create(
        output_image,
        xsize, ysize,
        nbands + 1,               # add 1 band for the angle
        gdal.GDT_Float32
    )

    out_dataset.GetRasterBand(1).SetDescription("VV")
    out_dataset.GetRasterBand(2).SetDescription("angle")

    out_dataset.SetGeoTransform(geotransform)
    out_dataset.SetProjection(proj)
    # ----------------------------------------------------------
    # ADD THE CONSTANT INCIDENCE-ANGLE BAND
    # ----------------------------------------------------------
    const_array = np.full((ysize, xsize), angle, dtype=np.float32)
    angle_band = out_dataset.GetRasterBand(nbands + 1)
    angle_band.WriteArray(const_array)
    #angle_band.SetDescription("angle")

    out_dataset.FlushCache()
    out_dataset = None


'''
def add_inc_angle_band(output_image, input_image, angle):
    dataset = gdal.Open(input_image, gdal.GA_ReadOnly)

    geotransform = dataset.GetGeoTransform()
    proj = dataset.GetProjection()
    xsize = dataset.RasterXSize
    ysize = dataset.RasterYSize
    nbands = dataset.RasterCount

    driver = gdal.GetDriverByName("GTiff")
    out_dataset = driver.Create(output_image, xsize, ysize, nbands+1, gdal.GDT_Float32)

    out_dataset.SetGeoTransform(geotransform)
    out_dataset.SetProjection(proj)

    in_band = dataset.GetRasterBand(1)
    data = in_band.ReadAsArray()
    out_band = out_dataset.GetRasterBand(1)
    out_band.WriteArray(data)
    out_band.SetDescription("VV")

    nodata = in_band.GetNoDataValue()
    if nodata is not None:
        out_band.SetNoDataValue(nodata)

    desc = in_band.GetDescription()
    if desc:
        out_band.SetDescription(desc)

    const_array = np.full((ysize, xsize), angle, dtype=np.float32)
    angle_band = out_dataset.GetRasterBand(2)
    angle_band.WriteArray(const_array)
    angle_band.SetDescription("angle")

    out_dataset.FlushCache()
    out_dataset = None
'''
