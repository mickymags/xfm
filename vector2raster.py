# This script converts a vector layer to a raster with all vectors having a value of 1.
# It also uses a reference raster to convert the vector layer


from osgeo import gdal, ogr

def vec2rast(vector_layer, ref_raster, output_layer_name):
    ref = gdal.Open(ref_raster)
    gt = ref.GetGeoTransform()
    proj = ref.GetProjection()
    cols = ref.RasterXSize
    rows = ref.RasterYSize

    drv = gdal.GetDriverByName("GTiff")
    out_ds = drv.Create(output_layer_name, cols, rows, 1, gdal.GDT_Int16)

    out_ds.SetGeoTransform(gt)
    out_ds.SetProjection(proj)

    band = out_ds.GetRasterBand(1)
    #band.SetNoDataValue(0)
    band.Fill(0)
    #out_ds.GetRasterBand(1).SetNoDataValue(0)

    vector_ds = ogr.Open(vector_layer)
    layer = vector_ds.GetLayer(0)

    gdal.RasterizeLayer(
        out_ds,
        [1],
        layer,
        burn_values=[1]#,
        #options=["ATTRIBUTE=class_id"]
    )

    band.FlushCache()
    out_ds.FlushCache()
