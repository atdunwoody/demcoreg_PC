from demcoreg import dem_align as da

def main():
    src_dems = [ r"C:\Users\alextd\Downloads\ELCMergedSurface_out.tif"
                
                ]    
        
    for src in src_dems:    
        kwargs = {
            'ref_dem_fn': r"C:\Users\alextd\Downloads\2024_DEM_usgsdef_co-navd88_outft.tif", # Source DEM to be aligned
            'src_dem_fn': src, # Fixed reference DEM against which others are aligned
            'mode': 'nuth', # Co-registration mode to use; choices= 'ncc', 'sad', 'nuth', 'none'
            'mask_list': [],  # choices = 'toa', 'snodas', 'modscag', 'bareground', 'glaciers', 'nlcd', 'none'. See demcoreg/dem_mask.py for more
            'max_offset': 100, # Maximum horizontal offset expected between DEMs, used to limit search space
            'max_dz': 100, # Maximum vertical difference allowed between DEMs before considered an outlier
            'slope_lim': (0.1, 40), # Range of surface slopes to consider in the alignment, outside values are disregarded
            'tiltcorr': True, # Whether to perform tilt correction as a post-process
            'polyorder': 1, # Order of polynomial used for tilt correction, if enabled
            'res': 'max', # Resolution strategy for the alignment; 'max' prioritizes the higher resolution of the two DEMs
            'max_iter': 30, # Maximum number of iterations to perform in seeking alignment  
            'tol': 0.02, # Tolerance threshold for iterative process; smaller changes than this will end the iteration
            'outdir': r"C:\Users\alextd\Documents\Test" # Output directory for aligned DEMs
        }
        da.dem_align(**kwargs)
    
        
if __name__ == "__main__":
    main()