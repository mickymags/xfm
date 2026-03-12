from osgeo import gdal, osr
import numpy as np

def string_finder(file, string_2_find):
    '''
    Finds a certain string within the metadata of an image file
    file is the path to the image file
    string_2_find is the metadata string you want to find
    '''
    my_info = gdal.Info(file)
    my_char = my_info.find(string_2_find)
    my_substring = my_info[my_char:my_char+100]
    index1 = my_substring.find('=')+1
    index2 = my_substring.find(' ')
    subsubstring = my_substring[index1:index2]
    return subsubstring

def geotransform(file):
    this_info = gdal.Info(file)
    gt = this_info[this_info.find('GeoTransform')+17:this_info.find('GeoTransform')+149] #147
    gt_split = gt.split(',')
    x = gt_split[2].split('\n')
    y = float(x[0].replace(' ', ''))
    z = float(x[1].replace(' ', ''))
    a = float(gt_split[1].replace(' ', ''))
    b = float(gt_split[3].replace(' ',''))
    c = float(gt_split[4].replace(' ',''))
    gt_v2 = [float(gt_split[0]), a, y, z, b, c]

    if gt_v2[2] == 0 and gt_v2[4] == 0:
        pixel_width = abs(gt_v2[1])
        pixel_height = abs(gt_v2[5])
    else:
        pixel_width = np.sqrt(gt_v2[1]**2 + gt_v2[2]**2)
        pixel_height = np.sqrt(gt_v2[4]**2 + gt_v2[5]**2)

    pixel_sizes = [pixel_width, pixel_height]
    return pixel_sizes


    #w_e_pixel_res = gt[gt.find(',')+1:-1]
    #w_e_pixel_res = w_e_pixel_res[0:w_e_pixel_res.find(',')]

    #n_s_pixel_res = gt[gt.find('Metadata')-22:gt.find('Metadata')]
    return gt_v2

def utc2local(file, input_time):
    file_info = gdal.Info(file)
    coords_char = file_info.find('Upper Left')
    coords = file_info[coords_char:coords_char+80]
    deg = int(coords[coords.find('(')+1:coords.find('.')])
    shift = np.floor(deg/15)

    acq_start_hours = input_time[input_time.find('T')+1:input_time.find(':')]
    ash_int = int(acq_start_hours)

    local_hours = ash_int + shift
    if local_hours < 0:
        local_hours = 0

    local_type = type(local_hours)
    if local_hours < 10:
        local_string = '0' + str(local_hours)
    else:
        local_string = str(local_hours)[0:2]

    #print(local_string)
    acq_local = input_time[0:input_time.find('T')] + 'T' + local_string + input_time[input_time.find(':'):-1]
    return acq_local
    #print('Acqusition Start Time (Approximate Local Solar Time)',acq_start_local)


def get_metadata(image):
    print('---------------------     Acquisition Time     ----------------------')
    print('\n')
    acq_start_utc = string_finder(image, 'ACQUISITION_START_UTC')
    print('Acquisition Start Time in UTC:', acq_start_utc)

    acq_start_local = utc2local(image, acq_start_utc)
    print('Approximate Local Acquisition Start Time:', acq_start_local, '\n')

    acq_end_utc = string_finder(image, 'ACQUISITION_END_UTC')
    print('Acquisition End Time in UTC', acq_end_utc)

    acq_end_local = utc2local(image, acq_end_utc)
    print('Approximate Local Acquisition End Time:', acq_end_local, '\n')

    print('----------------     Resolution and Pixel Size     -------------------')
    ds = gdal.Open(image)
    wkt = ds.GetProjection()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)

    srs.AutoIdentifyEPSG()
    epsg = srs.GetAuthorityCode(None)
    #print('Projection: EPSG', epsg, '\n')

    az_res = string_finder(image, 'AZIMUTH_RESOLUTION')
    print('Azimuth Resolution:', az_res)

    rg_res = string_finder(image, 'RANGE_RESOLUTION_CENTER')
    print('Range Resolution', rg_res)

    #gt = geotransform(image)
    #w_e_pixel_size = gt[0]
    #n_s_pixel_size = gt[1]
    #print('West-East Pixel Size (Degrees):', w_e_pixel_size, '\n')
    #print('North-South Pixel Size (Degrees):', n_s_pixel_size)

    #weps_meters = float(w_e_pixel_size) * 111111
    #nsps_meters = float(n_s_pixel_size) * 111111

    #print('\nApproximate West-East Pixel Size (meters):', weps_meters)
    #print('\nApproximate North-South Pixel Size (meters):', nsps_meters)

    az_nlooks = string_finder(image, 'AZIMUTH_LOOKS')
    print('Number of Looks in Azimuth', az_nlooks)

    rg_nlooks = string_finder(image, 'RANGE_LOOKS')
    print('Number of Looks in Range', rg_nlooks)


    print('----------------     Satellite Geometry      -------------------')

    inc_angle = string_finder(image, 'INCIDENCE_CENTER')
    print('Incidence Angle:', inc_angle)

    look_angle = string_finder(image, 'SATELLITE_LOOK_ANGLE')
    print('Look Angle:', look_angle)

    look_dir = string_finder(image, 'LOOK_SIDE')
    print('Look Direction', look_dir)

    orbit_dir = string_finder(image, 'ORBIT_DIRECTION')
    print('Orbit Direction', orbit_dir)

    print('----------------     General Metadata     -------------------')

    pol = string_finder(image, 'POLARIZATION')
    print('Polarization:', pol)

    chirp_bw = string_finder(image, 'CHIRP_BANDWIDTH')
    print('Chirp Bandwidth:', chirp_bw)

    acq_mode = string_finder(image, 'ACQUISITION_MODE')
    print('Imaging Mode', acq_mode)

    name = string_finder(image, 'SATELLITE_NAME')
    print('Satellite Name:', name)

    prod_lvl = string_finder(image, 'PRODUCT_LEVEL')
    print('Product Level', prod_lvl)

    prod_type = string_finder(image, 'PRODUCT_TYPE')
    print('Product Type', prod_type)
    return 0

def gcps2geotransform(image, output_filename):
    src_ds = gdal.Open(image, gdal.GA_ReadOnly)

    # Get GCPs and Projection
    gcps = src_ds.GetGCPs()
    gcp_projection = src_ds.GetGCPProjection()

    # Compute Geotransform grom gcps
    geotransform = gdal.GCPsToGeoTransform(gcps)

    if geotransform:
        # Create a copy of the dataset with a new geotransform
        driver = gdal.GetDriverByName("GTiff")
        dst_ds = driver.CreateCopy(output_filename, src_ds, 0)

        # Apply geotransform and projection
        dst_ds.SetGeoTransform(geotransform)
        dst_ds.SetProjection(gcp_projection)

        dst_ds = None
        print("Geotransform applied, file written to home directory")
    else:
        print("Failed.")

def rpc_warp(input_image, input_dem, proj_epsg, output_scale, output_filename):
    warp_options = gdal.WarpOptions(
        dstSRS = proj_epsg,
        rpc = True,
        xRes=output_scale,
        yRes=output_scale,
        resampleAlg='near',
        options=["RPC_DEM="+input_dem],
        targetAlignedPixels=True
    )

    gdal.Warp(output_filename, input_image, options=warp_options)


def get_inc_angle(image):
    info = gdal.Info(image)
    character = info.find("INCIDENCE_ANGLE")
    slice = info[character:character+50]
    print(info)
    #print(slice)
