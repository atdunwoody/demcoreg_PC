from demcoreg import dem_align as da

def main():
    src_dems = [
                r"C:\Users\alextd\Downloads\2024_DEM_usgsdef_co-navd88_outft.tif"
                ]    
        
    for src in src_dems:    
        kwargs = {   
        'ref_dem_fn': r"C:\Users\alextd\Downloads\ELCMergedSurface_out.tif",
        'src_dem_fn': src,
        'mode': 'nuth',
        'mask_list': [], 
        'max_offset': 100,
        'max_dz': 100,
        'slope_lim': (0.1, 40),
        'tiltcorr': False,
        'polyorder': 1,
        'res': 'max',
        'max_iter': 30,
        'tol': 0.02,
        'outdir': r"C:\Users\alextd"
        }
        da.dem_align(**kwargs)
        
        
    """    
    parser = argparse.ArgumentParser(description="Identify control surfaces for DEM co-registration") 
    parser.add_argument('dem_fn', type=str, help='DEM filename')
    parser.add_argument('--outdir', default=None, help='Directory for output products')
    parser.add_argument('--writeout', action='store_true', help='Write out all intermediate products, instead of only final tif')
    #parser.add_argument('-datadir', default=None, help='Data directory containing reference data sources (NLCD, bareground, etc)')
    parser.add_argument('--toa', action='store_true', help='Use top-of-atmosphere reflectance values (requires pregenerated "dem_fn_toa.tif")')
    parser.add_argument('--toa_thresh', type=float, default=0.4, help='Top-of-atmosphere reflectance threshold (default: %(default)s, valid range 0.0-1.0), mask values greater than this value')
    parser.add_argument('--snodas', action='store_true', help='Use SNODAS snow depth products')
    parser.add_argument('--snodas_thresh', type=float, default=0.2, help='SNODAS snow depth threshold (default: %(default)s m), mask values greater than this value')
    parser.add_argument('--modscag', action='store_true', help='Use MODSCAG fractional snow cover products')
    parser.add_argument('--modscag_thresh', type=float, default=50, help='MODSCAG fractional snow cover percent threshold (default: %(default)s%%, valid range 0-100), mask greater than this value')
    parser.add_argument('--bareground', action='store_true', help="Enable bareground filter")
    parser.add_argument('--bareground_thresh', type=float, default=60, help='Percent bareground threshold (default: %(default)s%%, valid range 0-100), mask greater than this value (only relevant for global bareground data)')
    parser.add_argument('--glaciers', action='store_true', help="Mask glacier polygons")
    parser.add_argument('--nlcd', action='store_true', help="Enable NLCD LULC filter (for CONUS)")
    nlcd_filter_choices = ['rock', 'rock+ice', 'rock+ice+water', 'not_forest', 'not_forest+not_water', 'none']
    parser.add_argument('--nlcd_filter', type=str, default='not_forest', choices=nlcd_filter_choices, help='Preserve these NLCD pixels (default: %(default)s)') 
    parser.add_argument('--dilate', type=int, default=None, help='Dilate mask with this many iterations (default: %(default)s)')
    return parser
    """
    
        
if __name__ == "__main__":
    main()